# Copyright (c) 2025 YycKop
# MIT License
# ai/ml_models/price_predictor.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import logging

# 获取当前模块的日志器
logger = logging.getLogger(__name__)


class PricePredictor:
    """
    农产品价格预测器
    基于随机森林算法的价格预测模型，支持分类变量处理和数值特征标准化
    """

    def __init__(self):
        """初始化价格预测器"""
        self.model = None  # 机器学习模型实例
        self.scaler = StandardScaler()  # 数值特征标准化器
        self.label_encoders = {}  # 分类变量编码器字典
        self.is_trained = False  # 模型训练状态标志

    def preprocess_data(self, df, categorical_columns):
        """
        数据预处理

        Args:
            df (pd.DataFrame): 输入数据框
            categorical_columns (list): 分类变量列名列表

        Returns:
            tuple: (处理后的数据框, 数值型列名列表)
        """
        df_processed = df.copy()  # 创建数据副本，避免修改原始数据

        # 处理分类变量：将文本类别转换为数值编码
        for col in categorical_columns:
            if col in df_processed.columns:
                # 如果该列还没有对应的编码器，创建新的LabelEncoder
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                # 使用编码器转换分类变量（确保转换为字符串类型避免类型错误）
                df_processed[col] = self.label_encoders[col].fit_transform(
                    df_processed[col].astype(str)
                )

        # 识别数值型变量列
        numerical_columns = df_processed.select_dtypes(include=[np.number]).columns.tolist()

        return df_processed, numerical_columns

    def train(self, X, y, categorical_columns=None, test_size=0.2):
        """
        训练价格预测模型

        Args:
            X (pd.DataFrame): 特征数据
            y (pd.Series): 目标变量（价格）
            categorical_columns (list, optional): 分类变量列名列表
            test_size (float, optional): 测试集比例，默认0.2（20%）

        Returns:
            dict: 训练结果字典，包含成功状态、评估分数和特征重要性
        """
        try:
            # 设置默认分类变量列表
            if categorical_columns is None:
                categorical_columns = []

            # 数据预处理
            X_processed, numerical_columns = self.preprocess_data(X, categorical_columns)

            # 标准化数值特征：使数值型特征具有零均值和单位方差
            if numerical_columns:
                X_processed[numerical_columns] = self.scaler.fit_transform(
                    X_processed[numerical_columns]
                )

            # 划分训练集和测试集
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y,
                test_size=test_size,  # 测试集比例
                random_state=42  # 随机种子，确保结果可重现
            )

            # 初始化随机森林回归模型
            self.model = RandomForestRegressor(
                n_estimators=100,  # 决策树数量
                max_depth=10,  # 树的最大深度，防止过拟合
                random_state=42,  # 随机种子
                n_jobs=-1  # 使用所有可用的CPU核心
            )

            # 训练模型
            self.model.fit(X_train, y_train)
            self.is_trained = True  # 更新训练状态

            # 评估模型性能
            train_score = self.model.score(X_train, y_train)  # 训练集R²分数
            test_score = self.model.score(X_test, y_test)  # 测试集R²分数

            logger.info(f"模型训练完成 - 训练集分数: {train_score:.4f}, 测试集分数: {test_score:.4f}")

            # 返回训练结果
            return {
                'success': True,
                'train_score': train_score,  # 训练集决定系数
                'test_score': test_score,  # 测试集决定系数
                'feature_importance': dict(  # 特征重要性字典
                    zip(X_processed.columns, self.model.feature_importances_)
                )
            }

        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def predict(self, X, categorical_columns=None):
        """
        使用训练好的模型进行价格预测

        Args:
            X (pd.DataFrame): 待预测的特征数据
            categorical_columns (list, optional): 分类变量列名列表

        Returns:
            np.array: 预测的价格数组

        Raises:
            ValueError: 如果模型未训练就尝试预测
        """
        # 检查模型是否已训练
        if not self.is_trained or self.model is None:
            raise ValueError("模型未训练，请先调用train方法")

        # 设置默认分类变量列表
        if categorical_columns is None:
            categorical_columns = []

        # 数据预处理（使用训练时保存的编码器）
        X_processed, numerical_columns = self.preprocess_data(X, categorical_columns)

        # 标准化数值特征（使用训练时的scaler进行转换，不是重新拟合）
        if numerical_columns:
            X_processed[numerical_columns] = self.scaler.transform(
                X_processed[numerical_columns]
            )

        # 进行预测
        predictions = self.model.predict(X_processed)

        return predictions

    def save_model(self, filepath):
        """
        保存训练好的模型到文件

        Args:
            filepath (str): 模型保存路径
        """
        if self.is_trained:
            # 打包所有模型相关数据
            model_data = {
                'model': self.model,  # 训练好的随机森林模型
                'scaler': self.scaler,  # 特征标准化器
                'label_encoders': self.label_encoders,  # 分类变量编码器
                'is_trained': self.is_trained  # 训练状态
            }
            # 使用joblib保存模型（适合存储scikit-learn模型）
            joblib.dump(model_data, filepath)
            logger.info(f"模型已保存到: {filepath}")

    def load_model(self, filepath):
        """
        从文件加载预训练模型

        Args:
            filepath (str): 模型文件路径
        """
        # 加载模型数据
        model_data = joblib.load(filepath)

        # 恢复模型状态
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.is_trained = model_data['is_trained']

        logger.info(f"模型已从 {filepath} 加载")