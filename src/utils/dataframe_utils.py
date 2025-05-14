import pandas as pd


class DataframeUtils:
    @staticmethod
    def columns_to_date(
        df: pd.DataFrame, columns: list[str], date_format: str = None
    ) -> pd.DataFrame:
        for col in columns:
            df[col] = pd.to_datetime(
                df[col], format=date_format, errors='coerce'
            )
        return df
