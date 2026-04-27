import datetime

class ZhejiangTOU2025:
    """浙江 2025 动态分时电价引擎 (严格修正版)"""
    def __init__(self):
        self.sharp_peak_months = [1, 7, 8, 12]
        self.deep_valley_dates = [
            "2025-01-28", "2025-01-29", "2025-01-30", # 春节示例
            "2025-05-01", "2025-05-02", "2025-05-03", # 五一示例
            "2025-10-01", "2025-10-02", "2025-10-03"  # 国庆示例
        ]

    def get_tou_vector(self, date_str: str) -> list:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        month = dt.month
        is_holiday = date_str in self.deep_valley_dates
        vector = ["未定义"] * 48

        for i in range(48):
            hour = (i + 1) * 0.5 # 映射为 0.5 到 24.0
            
            # 1. 基础逻辑
            if hour <= 8.0 or (11.0 < hour <= 13.0):
                vector[i] = "谷"
            elif hour > 17.0:
                vector[i] = "平"
            else:
                vector[i] = "峰"
                # 尖峰升级规则 (1,7,8,12月)
                if month in self.sharp_peak_months:
                    if (9.0 < hour <= 11.0) or (15.0 < hour <= 17.0):
                        vector[i] = "尖峰"

        # 2. 深谷覆盖逻辑 (最高优先级)
        if is_holiday:
            for i in range(48):
                hour = (i + 1) * 0.5
                if 10.0 < hour <= 14.0:
                    vector[i] = "深谷"

        return vector