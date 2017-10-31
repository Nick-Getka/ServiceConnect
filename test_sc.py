import unittest
from xml.etree import ElementTree
from serviceconnect.models import User
from serviceconnect import db, prep_app



class Testapp(unittest.TestCase):
    #Before and After Tests work
    @classmethod
    def setUpClass(self):
        self.app_temp = prep_app("TESTING")
        self.from_number = '+15555555555'
        self.from_zip = '20001'
        self.app = prep_app('TESTING')
        self.db = db
        self.client = self.app.test_client(self)
    @classmethod
    def tearDownClass(self):
        with self.app.app_context():
            user = self.db.session.query(User)\
                    .filter_by(zip_code=self.from_zip)\
                    .scalar()
            if user is not None:
                self.db.session.delete(user)
            self.db.session.commit()

    #Pretest and posttest work
    def setUp(self):
        pass
    def tearDown(self):
        pass

    #Assistant Functions
    def temp_user_exists(self, tdb):
        return tdb.session.query(User.phone_num)\
                    .filter_by(phone_num=self.from_number[2:])\
                    .scalar() is not None

    #Unit Tests
    def test_app(self):
        typology = ElementTree.parse('serviceconnect/typology.xml')
        root = typology.getroot()
        with self.app.app_context():
            #Testing New User
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'Test'
            })
            self.assertEqual(response.status, '200 OK')
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': '1234'
            })
            self.assertEqual(response.status, '200 OK')
            self.assertFalse(self.temp_user_exists(self.db))
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': self.from_zip
            })
            self.assertTrue(self.temp_user_exists(self.db))

            #Testing Direct Query - Bad Query
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'Test'
            })
            message = ElementTree.fromstring(response.data).find('Message')
            self.assertEqual(message.text, 'No information found on Test')

            #Testing Direct Query - Category
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'food'
            })
            message = ElementTree.fromstring(response.data).find('Message')
            answer = "Please text one of the following for information on the relevant sub category \n"
            target = None
            for child in root.iter() :
                if child.get('name') == 'food':
                    target = child
            self.assertIsNotNone(target)
            if target is not None:
                for sub in target.findall('service'):
                    answer += " {} - {} \n"\
                                .format(sub.get('name'), sub.text)
            self.assertEqual(message.text, answer)

            #Testing Direct Query - Final Data
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'free meals'
            })
            message = ElementTree.fromstring(response.data).find('Message')
            self.assertEqual(message.text, 'For more information on free meals at zip code 20001 see Free Meals Temp Data')

            #Testing Cancel
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'cancel textfood'
            })
            message = ElementTree.fromstring(response.data).find('Message')
            self.assertEqual(message.text, 'To comfirm cancellation please input your home zip code')
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'blah blah blah'
            })
            message = ElementTree.fromstring(response.data).find('Message')
            self.assertEqual(message.text[:18], 'Incorrect zip code')
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': 'cancel textfood'
            })
            response = self.client.post('/', data={
                'From': self.from_number,
                'Body': self.from_zip
            })
            self.assertEqual(response.status, '200 OK')
            self.assertFalse(self.temp_user_exists(self.db))



if __name__ ==  '__main__':
    unittest.main()
