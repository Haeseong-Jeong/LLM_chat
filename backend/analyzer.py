import pandas as pd
import os
from typing import Optional

class InOutAnalyzer:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.inbound_df = None
        self.outbound_df = None

    def load_all_data(self):
        inbound_list = []
        outbound_list = []

        for file in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, file)
            if not os.path.isfile(full_path):
                continue

            # 확장자에 따라 판다스로 읽기
            try:
                if file.endswith('.csv'):
                    df = pd.read_csv(full_path)
                elif file.endswith('.xlsx') or file.endswith('.xls'):
                    df = pd.read_excel(full_path)
                else:
                    continue  # 지원하지 않는 파일은 패스
            except Exception as e:
                print(f"[읽기 실패] {file}: {e}")
                continue

            # 파일명 기준 분류
            lower_file = file.lower()
            if lower_file.startswith('inbound') or lower_file.startswith('입고데이터'):
                inbound_list.append(df)
            elif lower_file.startswith('outbound') or lower_file.startswith('출고데이터'):
                outbound_list.append(df)

        # 데이터프레임 통합
        if inbound_list:
            self.inbound_df = pd.concat(inbound_list, ignore_index=True)
            self.inbound_df['Date'] = pd.to_datetime(self.inbound_df['Date'])
        else:
            print("입고 데이터가 없습니다.")

        if outbound_list:
            self.outbound_df = pd.concat(outbound_list, ignore_index=True)
            self.outbound_df['Date'] = pd.to_datetime(self.outbound_df['Date'])
        else:
            print("출고 데이터가 없습니다.")


    def numerical_data(self) -> Optional[pd.DataFrame]:
        # CSV 파일 불러오기 (파일 경로는 실제 파일에 맞게 수정하세요)
        #file_path = UPLOAD_DIR
        df = pd.read_csv(self.folder_path + '/한국중부발전(주)_BC유 재고 현황_20240816.csv', encoding='cp949')

        # 수치 데이터만 추출 (숫자형 컬럼만 선택)
        numeric_df = df.select_dtypes(include=['number'])

        return numeric_df



    def get_daily_summary(self) -> Optional[pd.DataFrame]:
        if self.inbound_df is None or self.outbound_df is None:
            print("먼저 load_all_data()를 실행하세요.")
            return None

        # 일별 집계
        inbound_summary = self.inbound_df.groupby('Date')['PalleteQty'].sum().reset_index()
        inbound_summary = inbound_summary.rename(columns={'PalleteQty': '입고량'})

        outbound_summary = self.outbound_df.groupby('Date')['PalleteQty'].sum().reset_index()
        outbound_summary = outbound_summary.rename(columns={'PalleteQty': '출고량'})

        # 병합
        summary = pd.merge(inbound_summary, outbound_summary, on='Date', how='outer').fillna(0)
        summary['입출고차이'] = summary['입고량'] - summary['출고량']
        return summary.sort_values(by='Date')


if __name__ == '__main__':
    analyzer = InOutAnalyzer('C:/Users/3sp39/Desktop/InOutBound/') 
    analyzer.load_all_data()
    summary = analyzer.get_daily_summary()
    print(summary)
