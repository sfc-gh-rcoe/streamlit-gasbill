import streamlit
import pandas as pd
import snowflake.connector
from snowflake.snowpark.session import Session

pd.option_context('display.float_format', '{:0.2f}'.format)
  
def create_sp_session():
  conn_param = {
    "account": streamlit.secrets["snowflake"].account,
    "user": streamlit.secrets["snowflake"].user,
    "database": streamlit.secrets["snowflake"].database,
    "role": streamlit.secrets["snowflake"].role,
    "warehouse": streamlit.secrets["snowflake"].warehouse,
    "schema": streamlit.secrets["snowflake"].schema,
    "password": streamlit.secrets["snowflake"].password
  }
  session = Session.builder.configs(conn_param).create()
  return session

def get_demo_table_list():
  with my_cnx.cursor() as my_cur:
      my_cur.execute("SELECT * FROM DEMO_TABLE")
      return my_cur.fetchall()

def get_demo_transaction_list():
  with my_cnx.cursor() as my_cur_transactions:
      my_cur_transactions.execute("SELECT *, YEAR(transactionDate) as transactionYear, MONTH(transactionDate) as transactionMonth FROM tbl_gasbill")
      return my_cur_transactions.fetchall()

def get_demo_transaction_list_sp(the_session, t_df):
  m_df = the_session.sql("SELECT *, YEAR(transactionDate) as transactionYear, MONTH(transactionDate) as transactionMonth FROM tbl_gasbill")
  t_df = m_df.to_pandas()
  # streamlit.table(t_df)
  return t_df.copy()

def get_demo_transaction_list_w_param_year(the_year):
  with my_cnx.cursor() as my_cur_transactions:
      my_cur_transactions.execute("SELECT *, YEAR(t_date) as transactionYear, MONTH(transactionDate) as transactionMonth FROM tbl_gasbill")
      return my_cur_transactions.fetchall()


# my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
my_session = create_sp_session()

# back_from_function = get_demo_table_list()
# my_cnx.close()

# df = pd.DataFrame(back_from_function, columns=['First', 'Last', 'Age'])
# streamlit.dataframe(df)


# streamlit.table(df)
r_df = pd.DataFrame()
back_from_transactions = get_demo_transaction_list_sp(my_session, r_df)
# my_cnx.close()



df_transactions = pd.DataFrame(back_from_transactions, columns=['TRANSACTIONDATE', 'TRANSACTIONAMOUNT', 'TRANSACTIONSTATUS', 'TRANSACTIONYEAR', 'TRANSACTIONMONTH'])
# streamlit.table(df_transactions)
df_transactions['TRANSACTIONDATE'] = pd.to_datetime(df_transactions['TRANSACTIONDATE'])
df_transactions['year'] = df_transactions['TRANSACTIONDATE'].dt.to_period('M')
# streamlit.table(df_transactions)
my_session.close()


df_m_rep = pd.DataFrame(df_transactions['TRANSACTIONMONTH'].unique().tolist(), columns = ['TRANSACTIONMONTH'])

df_y_rep = pd.DataFrame(df_transactions['TRANSACTIONYEAR'].unique().tolist(), columns = ['TRANSACTIONYEAR'])

filt_m = (df_transactions['TRANSACTIONMONTH'].isin(df_m_rep['TRANSACTIONMONTH'].values.tolist()))
# streamlit.write(filt_m)

filt_y = (df_transactions['TRANSACTIONYEAR'].isin(df_y_rep['TRANSACTIONYEAR'].values.tolist()))
# streamlit.write(filt_y)

df_months_represented = pd.DataFrame(df_transactions[filt_m], columns=['TRANSACTIONDATE', 'TRANSACTIONAMOUNT', 'TRANSACTIONSTATUS', 'TRANSACTIONYEAR', 'TRANSACTIONMONTH'])

# streamlit.table(df_months_represented.drop_duplicates(subset='TRANSACTIONMONTH'))

# streamlit.table(df_months_represented.drop_duplicates(subset='TRANSACTIONYEAR'))

df_sl_years = pd.DataFrame(df_months_represented)
# df_sl_years_0 = df_sl_years.to_frame().reset_index()
# df_sl_years_0 = df_sl_years_0.rename(columns={0: 'TRANSACTIONYEAR'})
# df_sl_years.set_index(['TRANSACTIONYEAR'], inplace=True)

streamlit.table(df_sl_years)

t_years = [int(x) for x in df_sl_years['TRANSACTIONYEAR']]
# t_years = (2015, 2016)

# streamlit.write(t_years)

# my_option = streamlit.selectbox("The Year: ", df_sl_years)

# filt_one = (df_transactions['TRANSACTIONYEAR'] == my_option)
# streamlit.table(df_transactions[filt_one])

# streamlit.write(t_years)

# streamlit.write(t_years)

streamlit.slider("Select a year", value = (int(df_sl_years['TRANSACTIONYEAR'].min()), int(df_sl_years['TRANSACTIONYEAR'].max())))
# df_sl_years
streamlit.title("Compare expenses associated between two years of natural gas bills:")
t_sel = streamlit.multiselect("What Years to compare?", df_sl_years, max_selections=2)

# streamlit.write(t_sel)

# streamlit.write(len(t_sel))

f_date_str = "%Y-%m-%d"
df_transactions['cv_TRANSACTIONDATE'] = df_transactions['TRANSACTIONDATE'].dt.strftime(f_date_str)
if len(t_sel) == 2:
  c1, c2 = streamlit.columns(2)

  c1.subheader("Year One: " + str(t_sel[0]))
  c2.subheader("Year Two: " + str(t_sel[1]))
  with c1:
    filt_c1 = (df_transactions['TRANSACTIONYEAR'] == t_sel[0])
    df_transactions_f1 = df_transactions[filt_c1].sort_values(by='TRANSACTIONDATE', ascending=False)
    streamlit.table(df_transactions_f1[['cv_TRANSACTIONDATE', 'TRANSACTIONAMOUNT']])
    df_transactions_f1.rename(columns={'TRANSACTIONAMOUNT': 'transactionAmount_1'}, inplace=True)

  with c2:
    filt_c2 = (df_transactions['TRANSACTIONYEAR'] == t_sel[1])
    df_transactions_f2 = df_transactions[filt_c2].sort_values(by='TRANSACTIONDATE', ascending=False)
    streamlit.table(df_transactions_f2[['cv_TRANSACTIONDATE', 'TRANSACTIONAMOUNT']])
    df_transactions_f2.rename(columns={'TRANSACTIONAMOUNT': 'transactionAmount_2'}, inplace=True)
 
  t_year1 = 'Year_' + str(t_sel[0])
  t_year2 = 'Year_' + str(t_sel[1])
 
  df_combined_trans = df_transactions_f1.merge(df_transactions_f2, how="inner", on='TRANSACTIONMONTH')
  df_combined_trans.rename(columns={'transactionAmount_1': t_year1, 'transactionAmount_2': t_year2}, inplace=True)
  # df_combined_trans = pd.DataFrame()
  # df_combined_trans['TRANSACTIONMONTH'] = df_transactions_f1['TRANSACTIONMONTH']
  # df_combined_trans['TRANSACTIONMONTH'] = df_transactions_f2['TRANSACTIONMONTH']
  # df_combined_trans['transactionAmount_1'] = df_transactions_f1['transactionAmount']
  # df_combined_trans['transactionAmount_2'] = df_transactions_f2['transactionAmount']
  streamlit.title("Merged DataFrame of the selected years:")
  # streamlit.table(df_combined_trans[['TRANSACTIONMONTH', 'Year_' + str(t_sel[0]), 'Year_' + str(t_sel[1])]].to_string(index=False))
  streamlit.table(df_combined_trans[['TRANSACTIONMONTH', 'Year_' + str(t_sel[0]), 'Year_' + str(t_sel[1])]])

  streamlit.line_chart(df_combined_trans, x= 'TRANSACTIONMONTH', y = [t_year1, t_year2])
  streamlit.write(df_combined_trans[['TRANSACTIONMONTH', 'Year_' + str(t_sel[0]), 'Year_' + str(t_sel[1])]].to_string(index=False))
