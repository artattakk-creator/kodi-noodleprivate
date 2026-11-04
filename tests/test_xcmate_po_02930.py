"""Gettext escape compatibility and real shipping DE/EN catalogs."""
import importlib.util,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('kodi_po_validator',ROOT/'tools/validate_kodi_po.py')
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)


class Po30Tests(unittest.TestCase):
    def test_all_shipping_catalogs_validate_utf8_and_contexts_match(self):
        catalogs=list((ROOT/'src/plugin.video.xtreammate/resources/language').glob('*/strings.po'))
        # .73 adds 15 deliberately partial catalogs: missing legacy entries
        # use English, while every new workflow entry must be translated.
        self.assertEqual(len(catalogs),17)
        contexts={p.parent.name:validator.validate(p.read_bytes().decode('utf-8')) for p in catalogs}
        english=contexts['resource.language.en_gb']
        self.assertEqual(english,contexts['resource.language.de_de'])
        self.assertIn('#34718',english)
        workflow={key for key in english if 38000<=int(key[1:])<38100}
        self.assertEqual(len(workflow),36)
        for name,keys in contexts.items():
            self.assertTrue(keys<=english,name)
            self.assertTrue(workflow<=keys,name)

    def test_json_unicode_escape_and_other_unknown_escapes_are_rejected(self):
        for bad in (r'\u2013',r'\U00002013',r'\q'):
            with self.assertRaises(validator.CatalogError):validator.validate('msgctxt "#1"\nmsgid "password '+bad+'"\nmsgstr "Passwort"\n')

    def test_literal_unicode_domain_backslash_quotes_and_continuations_are_valid(self):
        text='msgctxt "#1"\nmsgid "SMB – Gerät"\nmsgstr "Domain: '+r'DOMAIN\\user; \"Passwort\"\n'+'"\n"Fortsetzung"\n'
        self.assertEqual(validator.validate(text),{'#1'})
        self.assertEqual(validator.quoted(r'"DOMAIN\\user"'),'DOMAIN\\user')

    def test_duplicate_context_missing_translation_and_bad_quotes_are_rejected(self):
        good='msgctxt "#1"\nmsgid "One"\nmsgstr "Eins"\n'
        for text in (good+'\n'+good,'msgctxt "#1"\nmsgid "One"\n',good.replace('Eins','bad " quote')):
            with self.assertRaises(validator.CatalogError):validator.validate(text)


if __name__=='__main__':unittest.main()
