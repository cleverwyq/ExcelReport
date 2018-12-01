from urllib import request

import ssl
from xml.dom import minidom
ssl._create_default_https_context = ssl._create_unverified_context

class LoginB1AHManager:
    def __init__(self):
        self.user = "manager"
        self.pwd = "1234"
        self.company = "SBODEMOUS"
        self.b1ah_address = "10.58.114.74"
        self.https_port = 40000
        self.hana_port = 30015
        self.dom = None
        self.sld_location = ""
        self.data_sso = ""
        from http import cookiejar
        self.cookie_jar = cookiejar.CookieJar()
        self.opener = request.build_opener(
            request.HTTPCookieProcessor(self.cookie_jar))
        self.destination = ""
        self.data_saml = ""

    def login_step_1(self):
        print('begin login step 1')
        req = request.Request('https://{}:{}/IMCC/gate'.
                              format(self.b1ah_address, self.https_port))
        req.add_header("PAOS", "ver='urn:liberty:paos:2003-08' ;'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp'")
        req.add_header("Accept", "application/vnd.paos+xml")
        xml_string = ""
        with self.opener.open(req) as f:
            xml_string = f.read().decode('utf-8')
            print('response in step 1', xml_string)

        self.dom = dom = minidom.parseString(xml_string)
        root = dom.documentElement
        print('root :', root.nodeName)

        sld_node = root.getElementsByTagName("ns4:IDPEntry")[0]
        self.sld_location = sld_location = sld_node.getAttribute('Loc')
        print('sld location:', sld_location)

        header_node = root.getElementsByTagName("soap-env:Header")[0]

        while header_node.hasChildNodes():
            temp = header_node.childNodes[0]
            header_node.removeChild(temp)

        for child in header_node.childNodes:
            header_node.removeChild(child)
        self.data_sso = root.toxml(encoding='utf-8')
        print('remove header :', self.data_sso)
        print('======== End  Step 1 =============')
        return

    def login_step_2(self):
        print("begin step 2")
        url = self.sld_location.split('/')[2]
        sldLogonB1UserUrl = "https://{}/sld/sld.svc/LogonBySBOUser".format(url)
        print('user longon url:', sldLogonB1UserUrl)
        # sldLogonB1UserUrl="https://www.sina.com.cn"
        req = request.Request(sldLogonB1UserUrl)
        req.add_header('Content-Type', "application/json")

        data = '{{DBInstance:"{}:{}",CompanyDB:"{}"' \
               ',Account:"{}",Password:"{}"}}'.format(
                    self.b1ah_address,
                    self.hana_port,
                    self.company,
                    self.user,
                    self.pwd
                )
        with self.opener.open(req, data=data.encode('utf-8')) as f:
            # cookie = f.headers['Set-Cookie']
            response = f.read().decode('utf-8')
            print(response)

        print("======== End Step 2 ==============")
        return

    def login_step_3(self):
        print('begin login step 3')
        req = request.Request(self.sld_location)
        req.add_header("PAOS", "ver='urn:liberty:paos:2003-08' ;'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp'")
        req.add_header('Content-Type', "text/xml")

        sso = self.data_sso # .replace('\n','').replace('\t', '')

        # sso='<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Header></soap-env:Header><soap-env:Body><AuthnRequest AssertionConsumerServiceURL="https://10.58.114.74:40000/IMCC/saml2/sp/acs" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Destination="https://10.58.114.74:40000/sld/saml2/idp/sso" ID="S6267ae10-af13-4794-a457-c2ff5a797320" IssueInstant="2018-11-22T02:41:58.101Z" Version="2.0" xmlns="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:ns2="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:ns4="http://www.w3.org/2001/04/xmlenc#" xmlns:ns3="http://www.w3.org/2000/09/xmldsig#"><ns2:Issuer>https://10.58.114.74:40000/IMCC</ns2:Issuer></AuthnRequest></soap-env:Body></soap-env:Envelope>'
        with self.opener.open(req, data=sso) as f:
            response = f.read().decode('utf-8')
            response = response.replace('\n', '')
            print('response:', response)

        dom = minidom.parseString(response)
        root = dom.documentElement

        body_node = root.childNodes[1]
        self.destination = body_node.childNodes[0].getAttribute('Destination')
        print('destination:', self.destination)
        self.data_saml = response
        print("======= End Step 3 ===============")
        return

    def login_step_4(self):
        print('begin Step 4')
        req = request.Request(self.destination)
        req.add_header("PAOS", "ver='urn:liberty:paos:2003-08' ;'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp'")
        req.add_header('Content-Type', "text/xml")

        with self.opener.open(req, data=self.data_saml.encode('utf-8')) as f:
            response = f.read().decode('utf-8')
            print('response ', response)

        print('============ End Step 4 =============')

    def login(self):
        self.login_step_1()
        self.login_step_2()
        self.login_step_3()
        self.login_step_4()

    def run_imcc(self):
        req = request.Request("https://{}:{}/IMCC".format(self.b1ah_address, self.https_port))
        with self.opener.open(req) as f:
            response = f.read().decode('utf-8')
            print("in run_imcc() :", response)

    def run_excel_report(self, report_id, report_type):
        import uuid
        guid = uuid.uuid1()
        print('guid is:', guid)

        url = "https://{}:{}/IMCC/ia/report/{}".format(self.b1ah_address,
                                                  self.https_port, report_id)
        req = request.Request(url)
        data_boundary = str(guid)
        content_type = "multipart/form-data; boundary=\"" + data_boundary + "\""
        post_data = "--{}\r\nContent-Type: text/plain; charset=utf-8\r\n" \
                    "Content-Disposition: form-data; name=\"{}\"\r\n\r\n{}\r\n".format(
                    data_boundary, "type", report_type
                    )
        footer = "\r\n--" + data_boundary + "--\r\n"

        post_data += footer
        post_data = post_data.encode('utf-8')

        req.add_header('Content-Type', content_type)
        req.add_header('Content-Length', len(post_data))

        import datetime
        now = datetime.datetime.now()
        now = str(now)
        saved_report = 'demo-{}.xlsx'.format(now).\
            replace(' ', '+').replace(':', '+')

        with self.opener.open(req, data=post_data) as source:
            response = source.read()

            with open(saved_report, 'wb') as target:
                target.write(response)

        return saved_report

if __name__ == '__main__':
    manager = LoginB1AHManager()
    manager.login()
    # manager.run_imcc()
    manager.run_excel_report("25f2f05f-154b-4191-8392-252e60b30fb3",1)

