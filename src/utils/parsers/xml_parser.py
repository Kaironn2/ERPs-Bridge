import xml.etree.ElementTree as ET

import pandas as pd


class XMLParser:
    def xml_2003(xml_file, pop_footer=False) -> pd.DataFrame:
        namespaces = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
        tree = ET.parse(xml_file)
        root = tree.getroot()
        data_rows = []

        for row in root.findall('.//ss:Worksheet/ss:Table/ss:Row', namespaces):
            row_data = []
            for cell in row.findall('ss:Cell', namespaces):
                data = cell.find('ss:Data', namespaces)
                row_data.append(
                    data.text.strip() if data is not None and data.text else ''
                )
            data_rows.append(row_data)

        if pop_footer:
            data_rows.pop()

        column_names = data_rows[0] if data_rows else []
        df_mgt_xml = pd.DataFrame(data_rows[1:], columns=column_names)
        return df_mgt_xml
