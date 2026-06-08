from tools.yfinance_tools import get_company_profile, get_balance_sheet

print("hello")

print(get_company_profile.invoke({"ticker": "APOLLO"}))
print(get_balance_sheet.invoke({"ticker": "APOLLO"}))
# print(search_stock_news.invoke({"ticker": "INFY"}))
# print(search_india_macro_news.invoke({}))