# Mining Multi-Granularity Attribute Characteristics

本项目为该论文的代码开源，其中代码为整理后的代码，为了方便读者查看，对文件目录进行了调整改动。故在使用时 **可能** 存在导入包不存在等问题，读者仅需将文件目录加入用户路径或调整后进行使用即可。另外，本项目 **数据来源** 为 [Yago官网](https://yago-knowledge.org/) ，读者请自行下载到本地，再使用本项目中对应的文件进行处理。

## Installation

### Requirements

安装该项目 *./requirements.txt* 文件指定的依赖包，若使用 **shell** 命令，可参考下面代码。

```shell
pip install -r ./requirements.txt
```

**注：** 使用该命令时，注意路径问题。

### About data access

为方便本项目数据集读取操作，本项目在 *./ToolScript/* 目录下（为方便使用，读者可以将此路径存入电脑系统环境变量之中）封装了针对个人电脑读取 *SQL Server* 数据的类，读者在使用时，需要对该类当中的 `__init__()` 进行修改，本项目的初始化如下代码所示。

```python
class sql_tool:
    
    def __init__(self, database_name):
        self.DATABASE = database_name
        self.cnxn = None
        self.cursor = None
        self.server = '127.0.0.1'
        self.user = 'sa'
        self.password = '123456'
        self.engine = create_engine('mssql+pymssql://{}:{}@{}/{}' .format(self.user, self.password, self.server, self.DATABASE))
        pass
   pass
```

另外， *./ToolScript/test_script.ipynb* 展示了如何读取数据。 

**注：** 建议读者使用本项目提供的方式进行读取！否则在实际运行当中，可能会因为编码原因导致数据库数据存取时无限变动。

## Data storage

从 [Yago官网](https://yago-knowledge.org/) 下载得到的数据集为 *ttl* 格式文件，通过使用本项目的 *./Yago2SQL/Yago_into_Sql.ipynb* 或 *./Yago2SQL/yago_into_sql_server.py* 文件即可将 *ttl* 文件存储到本地的 *sql server 2012* 中。

**注：** 请读者注意更改相关参数，尤其注意连接数据库时相关参数的修改。

## Build Table

### Preparation work

本数据集中为自然语言数据集，故需要对其中每一个关键词进行编码，本项目使用 *./BuildTable/building_yago_code_tables.ipynb* 对数据集的自然语言关键词进行编码，此文件主要内容为，将 **yagoSchema, yagoCountTaxonomy, yagoTaxonomy, yagoDateFacts, yagoFacts, yagoLabels, yagoLiteralFacts, yagoTransitiveType** 数据转化成为 **instance_code, predicate_code, attribute_value_type_code, attribute_value_code** 。

### Multi-granularity table creation

本项目使用 *./BuildTable/building_concept_tables.ipynb* 建立所选取概念对应的 **binary, type, value** 三个粒度矩阵。

## Mining

### Run time calculation

当前项目分别使用 *./Mining/generate_binary_runtime.py, ./Mining/generate_type_runtime.py, ./Mining/generate_value_runtime.py* 三个脚本分别对 **bianry, type, value** 三个粒度分别使用 **Apriori, MDC** 算法在每个概念上的运行时间，另外使用 *./Mining/RuntimeAndPatternCount/concept_1_time.py, ./Mining/RuntimeAndPatternCount/concept_2_time.py, ./Mining/RuntimeAndPatternCount/concept_3_time.py, ./Mining/RuntimeAndPatternCount/concept_4_time.py* 四个脚本计算了每个概念在三个粒度上整体使用 **Apriori, MAC** 算法的运行时间，并生成了相关的 *excel* 文件。

### Number calculation

论文中计算了每个概念对应的所有频繁模式个数和极大频繁模式的个数，在本项目中分别使用 *./Mining/RuntimeAndPatternCount/concept_1.py, ./Mining/RuntimeAndPatternCount/concept_2.py, ./Mining/RuntimeAndPatternCount/concept_3.py, ./Mining/RuntimeAndPatternCount/concept_4.py* 对4个概念所有频繁模式和极大频繁模式分别进行了计算，并生成了相关的 *excel* 文件。

### Prediction

本项目使用 *./Mining/predict/concept_1.py, ./Mining/predict/concept_2.py, ./Mining/predict/concept_3.py, ./Mining/predict/concept_4.py* 分别对4个概念进行了概念预测，并生成了相关的 *excel* 文件。

## Other

论文中使用的 **Apriori, MDC** 算法源文件分别为 *./Mining/Apriori/apriori.py, ./Mining/maxFrequent/maxFrequent.py* 两个脚本，其次， **MAC** 为以上两个算法在三个粒度上的结合，故没有将该算法单独实现为一个源文件。若读者需要参考实现方法，请参考本项目中的 *./Mining/RuntimeAndPatternCount/common.py* 脚本中的 `Integ(concept_idx: int, frequent: float, return_type='pattern') -> list` 函数。

此项目代码开源为临时起意，故仅能对论文的相关实验代码进行整理后进行开源，没有封装执行文件，还请见谅！若读者希望重现，请仔细阅读当前文档。

# Personal statement

由于本人初次书写开源代码，水平有限，项目代码中可能存在部分问题，请读者见谅。若有问题，可在该网站上与本人联系。
