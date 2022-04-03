import unittest
from app import signup_test
from app import client_test
from app import client
from app import login
from app import quote_test
from app import app

class AppTest(unittest.TestCase):
    def test_sign_up(self):
        features = signup_test("", "", "")
        self.assertEqual(features[0], -1)
        self.assertEqual(features[1], -1)
        self.assertEqual(features[2], -1)
        self.assertEqual(features[3], True)

    def test_client(self):
        features = client_test("", "", 100*"add", "", "")
        self.assertEqual(features[0], "invalid")
        self.assertEqual(features[1], "invalid")
        self.assertEqual(features[2], "invalid")
        self.assertEqual(features[3], "invalid")
        self.assertEqual(features[4], "invalid")
        # TODO: Maybe check right range for invalid status and good status

    def test_quote(self):
        features = quote_test("not int", "", "", "not int", "not int")
        self.assertEqual(features[0], "invalid")
        self.assertEqual(features[1], "invalid")
        self.assertEqual(features[2], "invalid")
        self.assertEqual(features[3], "invalid")
        self.assertEqual(features[4], "invalid")

    def test_login(self):
        pass

class FlaskTestRoutes(unittest.TestCase):
    # checks that this route works and runs
    def test_idx(self):
        tester = app.test_client(self)
        response = tester.get("/login.html", follow_redirects=True)
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_log(self):
        tester = app.test_client(self)
        response = tester.post("/login.html", data={'loginid':'adam', 'loginpw':'abc123'})
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)

    def test_client_idx(self):
        tester = app.test_client(self)
        response = tester.get("/client.html", follow_redirects=True)
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
    
    def test_client_app(self):
        tester = app.test_client(self)
        response = tester.post("/client.html", data={'FullName':'full name', 'address':'10911 johnway Drive', 'address-2':'', 'city':'Houson', 'state':'TX', 'zipcode':'77012'})
        statuscode = response.status_code
        self.assertEqual(statuscode, 500)

    def test_signup_idx(self):
        tester = app.test_client(self)
        response = tester.get("/signup.html", follow_redirects=True)
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_signup_app(self):
        tester = app.test_client(self)
        response = tester.post("/signup.html", data={'username':'adam', 'password':'abc123', 'confirmpassword':'abc123'})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_quote_idx(self):
        tester = app.test_client(self)
        response = tester.get("/quote.html", follow_redirects=True)
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
    
    def test_quote_app(self):
        tester = app.test_client(self)
        response = tester.post("/quote.html", data={'gallon':220, 'delivery':'some address', 'datetime':'04-04-2022', 'price':500, 'totalamt':100000})
        statuscode = response.status_code
        self.assertEqual(statuscode, 500)



    

    



if __name__ == '__main__':
    unittest.main()