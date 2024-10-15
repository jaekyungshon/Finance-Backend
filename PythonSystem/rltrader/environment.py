
class Environment:
    PRICE_IDX = 4  # 종가의 위치

    def __init__(self, chart_data=None):
        self.chart_data = chart_data # 차트 데이터
        self.observation = None # 차트 데이터에서의 현재 위치 관측값
        self.idx = -1 # 현재 위치

    ### 차트 데이터의 처음 위치로 back ###
    def reset(self):
        self.observation = None
        self.idx = -1

    ### 하루 앞으로 이동하여, 차트 데이터에서 관측 데이터 제공 ###
    def observe(self):
        if len(self.chart_data) > self.idx + 1:
            self.idx += 1
            self.observation = self.chart_data.iloc[self.idx]
            return self.observation
        return None

    ### 관측 데이터로부터 종가 가져오기 ###
    def get_price(self):
        if self.observation is not None:
            return self.observation.iloc[self.PRICE_IDX]
        return None
    
    ### Setter ###
    def set_chart_data(self, chart_data):
        self.chart_data=chart_data