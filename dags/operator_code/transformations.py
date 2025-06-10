import pandas as pd

class CustomTransformations:
    @staticmethod
    def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna()

    @staticmethod
    def rename_columns(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
        return df.rename(columns=col_map)

    @staticmethod
    def filter_rows(df: pd.DataFrame, column: str, value) -> pd.DataFrame:
        return df[df[column] == value]

    # Add any other reusable transformations here
