# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/datasets/db_utils.py
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """数据库连接器"""

    @staticmethod
    def get_databases(connection_config):
        """获取所有数据库列表"""
        try:
            # 先连接到默认数据库（如 mysql）来获取数据库列表
            temp_config = connection_config.copy()
            temp_config['database'] = 'mysql'  # 或者 'information_schema'

            connection_string = DatabaseConnector.get_connection_string(temp_config)
            engine = create_engine(connection_string)

            with engine.connect() as conn:
                result = conn.execute(text("SHOW DATABASES"))
                databases = [row[0] for row in result]

            engine.dispose()
            return True, databases

        except Exception as e:
            logger.error(f"获取数据库列表失败: {str(e)}")
            return False, f"获取数据库列表失败: {str(e)}"

    @staticmethod
    def get_connection_string(connection_config):
        """根据配置生成数据库连接字符串"""
        db_type = connection_config.get('db_type', '').lower()

        if db_type == 'mysql':
            username = connection_config.get('username', '')
            password = connection_config.get('password', '')
            host = connection_config.get('host', 'localhost')
            port = connection_config.get('port', '3306')
            database = connection_config.get('database', '')
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

        elif db_type == 'postgresql':
            username = connection_config.get('username', '')
            password = connection_config.get('password', '')
            host = connection_config.get('host', 'localhost')
            port = connection_config.get('port', '5432')
            database = connection_config.get('database', '')
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"

        elif db_type == 'sqlite':
            database = connection_config.get('database', 'database.sqlite3')
            return f"sqlite:///{database}"

        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    @staticmethod
    def test_connection(connection_config):
        """测试数据库连接"""
        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            with engine.connect() as conn:
                # 执行简单查询测试连接
                conn.execute(text("SELECT 1"))

            engine.dispose()
            return True, "连接测试成功"

        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False, f"连接测试失败: {str(e)}"

    @staticmethod
    def get_tables(connection_config):
        """获取数据库中的所有表"""
        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            # 使用SQLAlchemy的inspect功能获取表信息
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            engine.dispose()
            return True, tables

        except Exception as e:
            logger.error(f"获取数据库表失败: {str(e)}")
            return False, f"获取表失败: {str(e)}"

    @staticmethod
    def get_table_schema(connection_config, table_name):
        """获取表结构信息"""
        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            inspector = inspect(engine)
            columns = inspector.get_columns(table_name)

            schema_info = []
            for column in columns:
                schema_info.append({
                    'name': column['name'],
                    'type': str(column['type']),
                    'nullable': column.get('nullable', True),
                    'primary_key': column.get('primary_key', False)
                })

            engine.dispose()
            return True, schema_info

        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return False, f"获取表结构失败: {str(e)}"

    @staticmethod
    def get_table_preview(connection_config, table_name, limit=10):
        """获取表数据预览"""
        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            # 使用pandas读取数据
            if connection_config.get('db_type') == 'mysql':
                query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
            else:
                query = f'SELECT * FROM "{table_name}" LIMIT {limit}'

            df = pd.read_sql(query, engine)

            engine.dispose()

            # 转换为字典格式
            data = df.to_dict('records')
            columns = df.columns.tolist()

            return True, {
                'columns': columns,
                'data': data,
                'total_rows': len(data),
                'preview_rows': len(data)
            }

        except Exception as e:
            logger.error(f"获取表数据预览失败: {str(e)}")
            return False, f"获取数据失败: {str(e)}"

    @staticmethod
    def get_table_row_count(connection_config, table_name):
        """获取表的行数"""
        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            if connection_config.get('db_type') == 'mysql':
                query = f"SELECT COUNT(*) as count FROM `{table_name}`"
            else:
                query = f'SELECT COUNT(*) as count FROM "{table_name}"'

            with engine.connect() as conn:
                result = conn.execute(text(query))
                count = result.scalar()

            engine.dispose()
            return True, count

        except Exception as e:
            logger.error(f"获取表行数失败: {str(e)}")
            return False, f"获取行数失败: {str(e)}"

    @staticmethod
    def import_table_data(connection_config, table_name, dataset_name, user, data_source):
        """导入表数据到数据集"""
        from .models import Dataset, DataRecord

        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            # 读取整个表
            if connection_config.get('db_type') == 'mysql':
                query = f"SELECT * FROM `{table_name}`"
            else:
                query = f'SELECT * FROM "{table_name}"'

            df = pd.read_sql(query, engine)
            engine.dispose()

            print(f"读取到 {len(df)} 条记录")  # 调试信息

            # 创建数据集
            dataset = Dataset.objects.create(
                name=dataset_name,
                data_source=data_source,  # 使用传入的 data_source 对象
                data_type='database',
                description=f'从数据库表 {table_name} 导入的数据，共 {len(df)} 条记录',
                data_structure={'fields': df.columns.tolist()},
                created_by=user
            )

            # 分批创建数据记录以避免内存问题
            batch_size = 100
            records_created = 0

            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                records = []

                for _, row in batch.iterrows():
                    records.append(DataRecord(
                        dataset=dataset,
                        data=row.to_dict()
                    ))

                DataRecord.objects.bulk_create(records)
                records_created += len(records)

                # 记录进度
                print(f"已导入 {records_created} 条记录")

            return True, f"成功导入 {records_created} 条记录", dataset.id

        except Exception as e:
            print(f"导入表数据失败: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return False, f"导入数据失败: {str(e)}", None

    @staticmethod
    def execute_query(connection_config, query, limit=100):
        """执行自定义查询"""
        try:
            connection_string = DatabaseConnector.get_connection_string(connection_config)
            engine = create_engine(connection_string)

            # 添加LIMIT子句（如果查询中没有）
            if 'LIMIT' not in query.upper():
                query += f" LIMIT {limit}"

            df = pd.read_sql(query, engine)
            engine.dispose()

            data = df.to_dict('records')
            columns = df.columns.tolist()

            return True, {
                'columns': columns,
                'data': data,
                'total_rows': len(data),
                'preview_rows': len(data)
            }

        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            return False, f"执行查询失败: {str(e)}"
