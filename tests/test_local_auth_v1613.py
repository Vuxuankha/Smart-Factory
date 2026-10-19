"""Targeted account/security regressions; all tests use temporary local DBs."""
import hashlib
import hmac
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from auth_local import AuthStore, AuthError, Session, hash_password, normalize_username, validate_password, default_auth_path, LOCK_SECONDS, ROLE_LABELS

PASS='SamplePass2026Safe!'
NEW_PASS='ChangedPass2027Safe!'

class AccountsV1613(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.db=Path(self.t.name)/'secure'/'accounts.sqlite3'
        self.now=[1000.0]
        self.store=AuthStore(self.db, clock=lambda:self.now[0])

    def bootstrap(self):
        self.store.register('rootadmin',PASS,'Root Admin')
        return self.store.authenticate('rootadmin',PASS)

    def approved(self,role='employee',name='worker1'):
        admin=self.bootstrap()
        self.store.register(name,PASS,name)
        self.store.approve(admin,name,role)
        return admin,self.store.authenticate(name,PASS)

    def test_01_first_run(self):self.assertTrue(self.store.first_run())
    def test_02_first_registration_admin(self):self.assertEqual(self.store.register('rootadmin',PASS),'admin_created')
    def test_03_subsequent_not_first_run(self):self.bootstrap();self.assertFalse(self.store.first_run())
    def test_04_admin_authenticated_role(self):self.assertEqual(self.bootstrap().role,'it_admin')
    def test_05_password_not_in_db_bytes(self):
        self.bootstrap();self.assertNotIn(PASS.encode(),self.db.read_bytes())
    def test_06_random_salt(self):
        a=hash_password(PASS);b=hash_password(PASS)
        self.assertNotEqual(a,b)
    def test_07_scrypt_hash_verifiable(self):
        salt,digest=hash_password(PASS)
        self.assertTrue(hmac.compare_digest(bytes.fromhex(digest),hashlib.scrypt(PASS.encode(),salt=bytes.fromhex(salt),n=2**14,r=8,p=1,dklen=32)))
    def test_08_case_insensitive_username(self):self.assertEqual(normalize_username(' Admin.01 '),'admin.01')
    def test_09_blank_username_rejected(self):
        with self.assertRaises(AuthError):normalize_username('')
    def test_10_username_with_space_rejected(self):
        with self.assertRaises(AuthError):normalize_username('bad account')
    def test_11_username_long_rejected(self):
        with self.assertRaises(AuthError):normalize_username('a'*70)
    def test_12_password_short_rejected(self):
        with self.assertRaises(AuthError):validate_password('short123')
    def test_13_password_requires_digit(self):
        with self.assertRaises(AuthError):validate_password('LettersOnlyLongEnough')
    def test_14_password_requires_letter(self):
        with self.assertRaises(AuthError):validate_password('1234567890123456')
    def test_15_control_rejected(self):
        with self.assertRaises(AuthError):validate_password('SomePassword123\n')
    def test_16_overlong_rejected(self):
        with self.assertRaises(AuthError):validate_password('A1'*130)
    def test_17_casefold_duplicate_blocked(self):
        self.store.register('rootadmin',PASS)
        with self.assertRaises(AuthError):self.store.register('ROOTADMIN',PASS)
    def test_18_registration_pending(self):
        self.bootstrap()
        self.assertEqual(self.store.register('operator2',PASS),'pending')
    def test_19_pending_cannot_login(self):
        self.bootstrap();self.store.register('operator2',PASS)
        with self.assertRaisesRegex(AuthError,'chưa được'):self.store.authenticate('operator2',PASS)
    def test_20_admin_approves_employee(self):
        _,user=self.approved();self.assertEqual(user.role,'employee')
    def test_21_admin_approves_auditor(self):
        _,user=self.approved('auditor');self.assertEqual(user.role,'auditor')
    def test_22_admin_approves_other_admin(self):
        _,user=self.approved('it_admin');self.assertTrue(user.allows('network'))
    def test_23_invalid_approval_role(self):
        admin=self.bootstrap()
        with self.assertRaises(AuthError):self.store.approve(admin,'rootadmin','hacker')
    def test_24_unknown_approval_rejected(self):
        admin=self.bootstrap()
        with self.assertRaises(AuthError):self.store.approve(admin,'missinguser')
    def test_25_employee_cannot_approve(self):
        _,user=self.approved()
        with self.assertRaises(PermissionError):self.store.approve(user,'rootadmin')
    def test_26_auditor_cannot_get_user_list(self):
        _,user=self.approved('auditor')
        with self.assertRaises(PermissionError):self.store.list_users(user)
    def test_27_admin_user_list_omits_hashes(self):
        admin=self.bootstrap();list_=self.store.list_users(admin)
        self.assertNotIn('password_hash',list_[0]);self.assertNotIn('salt',list_[0])
    def test_28_wrong_password_generic(self):
        self.bootstrap()
        with self.assertRaisesRegex(AuthError,'không đúng'):self.store.authenticate('rootadmin','bad')
    def test_29_unknown_account_generic(self):
        with self.assertRaisesRegex(AuthError,'không đúng'):self.store.authenticate('missinguser','bad')
    def test_30_bruteforce_lockout(self):
        self.bootstrap()
        for _ in range(5):
            with self.assertRaises(AuthError):self.store.authenticate('rootadmin','bad')
        with self.assertRaisesRegex(AuthError,'tạm khóa'):self.store.authenticate('rootadmin',PASS)
    def test_31_lockout_persists_new_store(self):
        self.bootstrap()
        for _ in range(5):
            with self.assertRaises(AuthError):self.store.authenticate('rootadmin','bad')
        new_store=AuthStore(self.db,clock=lambda:self.now[0])
        with self.assertRaisesRegex(AuthError,'tạm khóa'):new_store.authenticate('rootadmin',PASS)
    def test_32_lock_expires(self):
        self.bootstrap()
        for _ in range(5):
            with self.assertRaises(AuthError):self.store.authenticate('rootadmin','bad')
        self.now[0]+=LOCK_SECONDS+1
        self.assertEqual(self.store.authenticate('rootadmin',PASS).username,'rootadmin')
    def test_33_change_password(self):
        admin=self.bootstrap();self.store.change_password(admin,PASS,NEW_PASS)
        self.assertEqual(self.store.authenticate('rootadmin',NEW_PASS).username,'rootadmin')
        with self.assertRaises(AuthError):self.store.authenticate('rootadmin',PASS)
    def test_34_wrong_old_password_blocks_change(self):
        admin=self.bootstrap()
        with self.assertRaises(AuthError):self.store.change_password(admin,'wrong',NEW_PASS)
        self.assertEqual(self.store.authenticate('rootadmin',PASS).username,'rootadmin')
    def test_35_admin_cannot_deactivate_self(self):
        admin=self.bootstrap()
        with self.assertRaises(AuthError):self.store.deactivate(admin,'rootadmin')
    def test_36_last_admin_cannot_demote_self(self):
        admin=self.bootstrap()
        with self.assertRaises(AuthError):self.store.approve(admin,'rootadmin','employee')
    def test_37_disable_user_rejects_auth(self):
        admin,user=self.approved()
        self.store.deactivate(admin,'worker1')
        with self.assertRaisesRegex(AuthError,'chưa được'):self.store.authenticate('worker1',PASS)
    def test_38_revoke_session_after_disable(self):
        admin,user=self.approved()
        self.assertTrue(self.store.session_current(user))
        self.store.deactivate(admin,'worker1')
        self.assertFalse(self.store.session_current(user))
    def test_39_revoke_session_after_role_change(self):
        admin,user=self.approved()
        self.store.approve(admin,'worker1','auditor')
        self.assertFalse(self.store.session_current(user))
    def test_40_employee_no_network(self):
        self.assertFalse(Session('x','employee','X').allows('network'))
    def test_41_auditor_no_mutate_pmc(self):
        self.assertFalse(Session('x','auditor','X').allows('pmc'))
    def test_42_admin_network(self):
        self.assertTrue(Session('x','it_admin','X').allows('network'))
    def test_43_audit_no_passwords(self):
        admin=self.bootstrap()
        logs=self.store.audit_events(admin)
        self.assertTrue(logs)
        self.assertNotIn(PASS,repr(logs))
    def test_44_employee_no_audit_access(self):
        _,user=self.approved()
        with self.assertRaises(PermissionError):self.store.audit_events(user)
    def test_45_store_directory_created(self):
        self.assertTrue(self.db.is_file())
    def test_46_private_storage_on_posix(self):
        if os.name!='posix':self.skipTest('POSIX')
        self.assertEqual(self.db.stat().st_mode & 0o077,0)
        self.assertEqual(self.db.parent.stat().st_mode & 0o077,0)
    def test_47_env_override(self):
        with patch.dict(os.environ,{'ALIBABA_OPERATIONS_DATA':self.t.name}):
            self.assertEqual(default_auth_path(),Path(self.t.name)/'accounts.sqlite3')
    def test_48_unknown_role_nopermission(self):
        self.assertFalse(Session('x','anything','X').allows('mail'))
    def test_49_no_password_field_session(self):
        self.assertNotIn('password',self.bootstrap().__dict__)
    def test_51_invalid_name_cannot_alias_real_username(self):
        self.store.register('invalid',PASS)
        with self.assertRaises(AuthError):
            self.store.authenticate('bad name that is invalid',PASS)

    def test_50_approved_by_logged(self):
        admin,_=self.approved()
        rows=self.store.list_users(admin)
        self.assertEqual([r for r in rows if r['username']=='worker1'][0]['approved_by'],'rootadmin')

if __name__=='__main__':unittest.main()
