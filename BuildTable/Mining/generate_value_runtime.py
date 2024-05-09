import time
import warnings
from Parameter import *
from Apriori.apriori import Apriori
from ToolScript.readSql import sql_tool
from maxFrequent.maxFrequent import maxFrequent

warnings.filterwarnings('ignore')


yc_tool = sql_tool('YagoCore')


for frequent in Freq_list_3:
    print('Frequent is {}:' .format(frequent))
    for i in range(1, 5):
        # for ttype in TABLE_TYPE_LIST:
        ttype = 'value'
        table_name = 'concept_%d_' % i + ttype
        table = yc_tool.get_table(table_name).iloc[:, 2:]
        print('{}:' .format(table_name))
        apri = Apriori(frequent)
        mxfq = maxFrequent(frequent)
        apri.predict(table), mxfq.predict(table)
        print('apri runtime: {}, mxfq runtime: {}' .format(apri.runtime, mxfq.runtime))

