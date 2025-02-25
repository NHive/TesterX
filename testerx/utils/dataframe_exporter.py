import pandas as pd
import io


class DataFrameToStringConverter:
    """
    用于将 Pandas DataFrame 转换为字符串的类，以便输入到大型模型。

    支持自定义分隔符、是否包含标题行等选项。
    """

    def __init__(self, col_sep=',', row_sep='\n', include_header=True, index=False):
        """
        初始化 DataFrameToStringConverter。

        Args:
            col_sep (str): 列分隔符，默认为逗号 (',')。
            row_sep (str): 行分隔符，默认为换行符 ('\n')。
            include_header (bool): 是否包含标题行，默认为 True。
            index (bool): 是否包含索引列，默认为 False。
        """
        self.col_sep = col_sep
        self.row_sep = row_sep
        self.include_header = include_header
        self.index = index

    def convert_to_string(self, df: pd.DataFrame) -> str:
        """
        将 DataFrame 转换为字符串。

        Args:
            df (pd.DataFrame): 要转换的 Pandas DataFrame。

        Returns:
            str: DataFrame 的字符串表示形式。
        """
        output_buffer = io.StringIO()  # 使用StringIO 避免直接操作文件，提高效率

        df.to_csv(
            output_buffer,
            sep=self.col_sep,
            lineterminator=self.row_sep,  # 更正为 lineterminator
            header=self.include_header,
            index=self.index
        )

        return output_buffer.getvalue()


# 示例用法
if __name__ == '__main__':
    # 创建一个示例 DataFrame
    data = {'姓名': ['张三', '李四', '王五'],
            '年龄': [25, 30, 28],
            '城市': ['北京', '上海', '广州']}
    df = pd.DataFrame(data)

    # 创建 DataFrameToStringConverter 实例
    converter = DataFrameToStringConverter()  # 使用默认参数

    # 将 DataFrame 转换为字符串
    string_output = converter.convert_to_string(df)
    print("默认转换 (逗号分隔, 包含标题):")
    print(string_output)

    print("-" * 20)

    # 使用自定义参数
    converter_tab_sep = DataFrameToStringConverter(col_sep='\t', row_sep='\n\n', include_header=False, index=True)
    string_output_tab = converter_tab_sep.convert_to_string(df)
    print("自定义转换 (Tab分隔, 不包含标题, 包含索引):")
    print(string_output_tab)
