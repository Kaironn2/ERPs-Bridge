import pandas as pd
from django.utils.timezone import make_aware


class DataframeUtils:
    @staticmethod
    def columns_to_date(
        df: pd.DataFrame, columns: list[str], date_format: str = None
    ) -> pd.DataFrame:
        for col in columns:
            df[col] = pd.to_datetime(
                df[col], format=date_format, errors='coerce'
            )
            df[col] = df[col].apply(
                lambda dt: make_aware(dt)
                if pd.notnull(dt) and dt.tzinfo is None
                else dt
            )
        return df
