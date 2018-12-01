import pyhdb

class DBManager(object):
    instance = None

    @staticmethod
    def get_instance():
        if DBManager.instance is None:
            DBManager.instance = DBManager()
        return DBManager.instance

    def __init__(self):
        self.hana_address = "10.58.114.74"
        self.schema = "SBODEMOUS"
        self.port = 30015
        self.connection = None
        self.connection = pyhdb.connect(host=self.hana_address,
                                        port=self.port,
                                        user="SYSTEM",
                                        password="manager")

    def retrieve_report_list(self):

        cursor = self.connection.cursor()
        sql = 'SELECT "ReportId", "Title" FROM {}.OIRD ' \
              'WHERE "Type"=1'.format(self.schema)
        try:
            cursor.execute(sql)
            query_result = cursor.fetchall()
        except Exception as exp:
            print("oops! Exception occurs:" , exp)
            return None

        context = dict()
        for (rid, rname) in query_result:
            context[rid] = rname

        # self.connection.close()
        return context

    def retrieve_view_measures(self):
        cursor = self.connection.cursor()
        sql = 'SELECT "MEASURE_NAME" FROM  "_SYS_BI"."BIMC_MEASURES" ' \
              'where catalog_name like \'sap.{}%\' and ' \
              'cube_name like \'SalesAnalysisQuery\' ' \
              'Order by MEASURE_NAME'.format(self.schema.lower())
        print("Get report measures:{}".format(sql))
        try:
            cursor.execute(sql)
            measures = cursor.fetchall()
            mesures_list = list()
            for (m,) in measures:
                mesures_list.append(m)

            return mesures_list
        except Exception as exp:
            print("Opps! Exception ->", exp)
            return list()

    def retrieve_view_dimensions(self):
        cursor = self.connection.cursor()
        sql = 'SELECT DIMENSION_NAME FROM "_SYS_BI"."BIMC_ALL_DIMENSIONS" ' \
              'where catalog_name like \'sap.{}%\' and cube_name ' \
              'like \'SalesAnalysisQuery\' and ' \
              '"DIMENSION_TYPE"=3 ORDER BY DIMENSION_NAME'.format(self.schema.lower())
        print("fetch dimensions: ", sql)

        sql = 'SELECT P."COLUMN_NAME", P."DESCRIPTION", P."COLUMN_SQL_TYPE", D."DIMENSION_NAME", ' \
              'D."DIMENSION_CAPTION", D."IS_PRIVATE_ATTRIBUTE", D."DIMENSION_ORDINAL" AS "D_ORDER" ' \
              'FROM "_SYS_BI"."BIMC_PROPERTIES" P INNER JOIN "_SYS_BI"."BIMC_DIMENSIONS" D ' \
              'ON P."CATALOG_NAME"=D."CATALOG_NAME" AND P."SCHEMA_NAME"=D."SCHEMA_NAME" AND ' \
              'P."CUBE_NAME"=D."CUBE_NAME" AND P."DIMENSION_UNIQUE_NAME"=D."DIMENSION_UNIQUE_NAME" ' \
              'WHERE P."CATALOG_NAME"=\'sap.{}.ar.case\' AND P."CUBE_NAME"=\'SalesAnalysisQuery\' AND P."PROPERTY_TYPE"=4 ' \
              'AND P."IS_PRIVATE_ATTRIBUTE" IN (0, 1)  AND D."DIMENSION_NAME" <> \'Measures\' ' \
                'ORDER BY P."COLUMN_NAME"'.format(self.schema.lower())
        try:
            cursor.execute(sql)
            dimensions = cursor.fetchall()
            dimension_list = list()
            for (d,p1,p2,p3,p4,p5,p6) in dimensions:
                dimension_list.append(d)
            return dimension_list

        except Exception as exp:
            print("Opps! -> ", exp)
            return list()

    def update_report_definition(self, report_definition, name=None):
        if name is None:
            name = 'demox.xlsx'

        import os.path
        if not os.path.exists(name):
            print("Opps, report template not exists!!!")
            return

        from pyhdb import Blob
        blob1 = None
        with open(name, 'rb') as f:
            template = f.read()
            blob1 = Blob(template)
        blob0 = Blob(report_definition.encode(encoding='utf-8'))

        cursor = self.connection.cursor()
        sql0 = 'UPDATE {}.OIRD SET "Definition"=:1 WHERE "ReportId" like \'abcdabcd-%\''.format(self.schema)
        sql1 = 'UPDATE {}.IRD1 SET "Template"=:1 WHERE "ReportId" like \'abcdabcd-%\''.format(self.schema)

        try:
            print("execute {}".format(sql0))
            cursor.execute(sql0, [blob0])
            count = cursor.rowcount
            print("{} report in OIRD updated".format(count))
            count = cursor.execute(sql1, [blob1]).rowcount
            print("{} report in IRD1 updated".format(count))
            self.connection.commit()
            return True
        except Exception as exp:
            print("Opss!,when update report template =>")
            print(exp)
            return False

if __name__ == '__main__':
    db = DBManager()
    # context = db.retrieve_report_list()
    context = db.update_report_definition("<xml></de>")
    print(context)
