from django.http import HttpResponse
from .FolderItem import FolderItem


class UploadedItem:
    def __init__(self):
        self.name = ""
        self.web_url = ""


class GraphAPIManager:
    token_type = ""
    access_token = ""
    refresh_token = ""
    instance = None

    def __init__(self):
        if len(GraphAPIManager.access_token) == 0:
            import os.path
            if os.path.exists("token.bin"):
                with open('token.bin', 'r') as f:
                    file_content = f.read()
                    arr = file_content.split(' ')
                    GraphAPIManager.access_token = arr[0]
                    GraphAPIManager.token_type = arr[1]

    @staticmethod
    def getInstance():
        if GraphAPIManager.instance is None:
            GraphAPIManager.instance = GraphAPIManager()
        return GraphAPIManager.instance

    def retrieve_report_template(self, name=None):
        if name is None:
            name = 'demox.xlsx'

        import http.client
        conn = http.client.HTTPSConnection("graph.microsoft.com")
        relative_url = "/v1.0/me/drive/root:/{}:/content".format(name)

        headers = dict()
        headers['Authorization'] = GraphAPIManager.token_type + " " \
                                   + GraphAPIManager.access_token
        conn.request(method="GET", url=relative_url, headers=headers)
        response = conn.getresponse()
        print("Download: response code {}".format(response.code))

        url = response.headers['Location']
        url = url[8:]
        arr = url.split('/')
        host = arr[0]
        relative_file_url = '/'+arr[1]
        conn1 = http.client.HTTPSConnection(host)
        conn1.request(method="GET", url=relative_file_url)
        response = conn1.getresponse()

        with open("demox.xlsx", "wb") as f:
            f.write(response.read())

    def retrieve_root_directory(self):
        import http.client

        conn = http.client.HTTPSConnection("graph.microsoft.com")
        relative_url = "/v1.0/me/drive/root/children"
        headers = dict()
        headers['Authorization'] = GraphAPIManager.token_type + " " \
                                   + GraphAPIManager.access_token
        conn.request(method="GET", url=relative_url, headers=headers)
        response = HttpResponse(conn.getresponse())
        print("Retrive Directory Response")
        print(response.content)

        content = str(response.content, encoding='utf-8')
        import json
        directory_info = json.loads(content)
        folders = directory_info.get('value')
        if folders is not None:
            folder_list = list()
            for f in folders:
                display_name = f.get('name')
                if f.get('folder') is None:
                    is_folder = True
                else:
                    is_folder = False

                item = FolderItem()
                item.set_display_name(display_name)
                item.set_is_folder(is_folder)
                folder_list.append(item)

            return folder_list
        else:
            # Todo: Use refresh token
            return list()


    def upload_excel_report(self, report_name):
        file_name = report_name.split('/')[-1]
        relative_url = "/v1.0/me/drive/items/{}:/{}:/content". \
            format("root", file_name + ".xlsx")

        import http.client
        conn = http.client.HTTPSConnection('graph.microsoft.com')
        headers = dict()
        headers['Content-Type'] = "application/vnd.openxmlformats-" \
                                  "officedocument.spreadsheetml.sheet"
        headers['Authorization'] = GraphAPIManager.token_type + " " \
                                   + GraphAPIManager.access_token

        body = open(report_name, 'rb')

        conn.request(method='PUT', url=relative_url, body=body, headers=headers)
        response = HttpResponse(conn.getresponse())

        content = str(response.content, encoding='utf-8')
        return content

    @staticmethod
    def extract_uploaded_file_info(response_content):
        import json
        upload_info_dict = json.loads(response_content)
        upload_item = UploadedItem()
        upload_item.web_url = upload_info_dict.get('webUrl')
        upload_item.name = upload_info_dict.get('name')

        return upload_item
