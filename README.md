[![](https://img.shields.io/badge/语言切换-中文-blue)](./README_cn.md)

# Mining Multi-Granularity Attribute Characteristics

This project contains the open-source code for the paper. The code provided here has been organized for easier reference. Therefore, **potential** issues such as missing package imports may arise due to adjustments made to the file directory. Readers simply need to add the file directory to their user path or make necessary adjustments before use.

Additionally, the **data source** for this project is [Yago's official website](https://yago-knowledge.org/). Readers are required to download the data to their local environment and then utilize the corresponding files provided within this project for processing.

## Installation

### Requirements

To install the dependencies specified in the *./requirements.txt* file for this project, if utilizing **shell** commands, you can refer to the code snippet below:

```shell
pip install -r ./requirements.txt
```

**Note:** Pay attention to path-related issues when using this command.

### About data access

For the convenience of dataset retrieval operations in this project, under the *./ToolScript/* directory (for ease of use, readers can add this path to their computer's system environment variables), classes tailored for reading *SQL Server* data for personal computers have been encapsulated. When using this, readers need to modify the `__init__()` method within this class. The initialization of this project is as shown in the following code snippet.

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

Additionally, *./ToolScript/test_script.ipynb* demonstrates how to read the data.

**Note:** It is recommended that readers utilize the methods provided in this project for data retrieval. Otherwise, during actual execution, there may be infinite variations in database data retrieval due to encoding issues.

## Data storage

The dataset obtained from [Yago's official website](https://yago-knowledge.org/) is in *ttl* format. You can use either the *./Yago2SQL/Yago_into_Sql.ipynb* notebook or the *./Yago2SQL/yago_into_sql_server.py* script from this project to store the *ttl* file into your local *SQL Server 2012*.

**Note:** Please pay attention to modifying relevant parameters, especially when adjusting parameters related to database connections.

## Build Table

### Preparation work

In this dataset, since it contains natural language data, it's necessary to encode each keyword. This project utilizes *./BuildTable/building_yago_code_tables.ipynb* to encode the natural language keywords in the dataset. The main content of this file involves transforming **yagoSchema, yagoCountTaxonomy, yagoTaxonomy, yagoDateFacts, yagoFacts, yagoLabels, yagoLiteralFacts, yagoTransitiveType** data into **instance_code, predicate_code, attribute_value_type_code, attribute_value_code**.

### Multi-granularity table creation

This project utilizes *./BuildTable/building_concept_tables.ipynb* to establish three matrices corresponding to the selected concepts: **binary, type,** and **value**.

## Mining

### Run time calculation

The current project utilizes three scripts: *./Mining/generate_binary_runtime.py, ./Mining/generate_type_runtime.py, ./Mining/generate_value_runtime.py*, to measure the runtime of **binary, type, value** matrices respectively using the **Apriori** and **MDC** algorithms on each concept. Additionally, four scripts: *./Mining/RuntimeAndPatternCount/concept_1_time.py, ./Mining/RuntimeAndPatternCount/concept_2_time.py, ./Mining/RuntimeAndPatternCount/concept_3_time.py, ./Mining/RuntimeAndPatternCount/concept_4_time.py*, are used to calculate the overall runtime of each concept on the three granularities using **Apriori** and **MAC** algorithms, and generate corresponding *excel* files.

### Number calculation

In the paper, the number of all frequent patterns and maximal frequent patterns corresponding to each concept was calculated. In this project, *./Mining/RuntimeAndPatternCount/concept_1.py, ./Mining/RuntimeAndPatternCount/concept_2.py, ./Mining/RuntimeAndPatternCount/concept_3.py, ./Mining/RuntimeAndPatternCount/concept_4.py* scripts are used to compute all frequent patterns and maximal frequent patterns for the four concepts respectively, and generate relevant *excel* files.

### Prediction

This project utilizes *./Mining/predict/concept_1.py, ./Mining/predict/concept_2.py, ./Mining/predict/concept_3.py, ./Mining/predict/concept_4.py* to perform concept prediction for the four concepts respectively, and generates relevant *excel* files.

## Other

The source files for the **Apriori** and **MDC** algorithms used in the paper are respectively *./Mining/Apriori/apriori.py* and *./Mining/maxFrequent/maxFrequent.py*. Additionally, **MAC** is a combination of the above two algorithms on three granularities, so it's not implemented as a separate source file. If readers need to refer to the implementation method, they can check the `Integ(concept_idx: int, frequent: float, return_type='pattern') -> list` function in the *./Mining/RuntimeAndPatternCount/common.py* script of this project.

This project's code was open-sourced on a temporary basis, hence only the experimental code related to the paper could be organized and made open-source. There are no packaged executable files, so please forgive us for this inconvenience! If readers wish to reproduce the experiments, please carefully read the current document.

# Personal statement

Due to my limited experience in writing open-source code, there may be some issues in the project code. I apologize for any inconvenience this may cause to the readers. If there are any problems, please feel free to contact me through this website.
