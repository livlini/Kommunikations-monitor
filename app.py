import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title='CFO Communication Monitor', page_icon='📡', layout='wide')

st.title('📡 CFO Communication Monitor')
st.caption('Weekly intelligence for CFO · Audit · Tax · AI')

DATA = [
    {'Trend':'AI governance & AI Act','Category':'AI','Score':91,'WoW':'+38%','Signals':18,'Sources':5,'Why':'Regulation and governance are moving from principles into operational compliance and supervision.','Angle':'What should CFOs have in place before scaling AI across finance?','Format':'LinkedIn · Event · Newsletter'},
    {'Trend':'AI in the finance function','Category':'CFO','Score':88,'WoW':'+31%','Signals':16,'Sources':4,'Why':'AI is increasingly discussed as a finance transformation tool rather than a standalone technology experiment.','Angle':'From AI pilots to measurable value in the finance function.','Format':'LinkedIn · Article'},
    {'Trend':'Audit standards & assurance','Category':'Audit','Score':74,'WoW':'+14%','Signals':12,'Sources':3,'Why':'Professional guidance and standards continue to change, creating a need for concise client communication.','Angle':'Three assurance developments finance leaders should know this quarter.','Format':'Newsletter · Article'},
    {'Trend':'Digital tax & e-invoicing','Category':'Tax','Score':70,'WoW':'+12%','Signals':10,'Sources':4,'Why':'Tax reporting is becoming increasingly digital and data-driven, affecting processes and controls.','Angle':'Is your finance function ready for increasingly digital tax reporting?','Format':'Event · LinkedIn'},
    {'Trend':'Finance automation','Category':'CFO','Score':66,'WoW':'+9%','Signals':9,'Sources':4,'Why':'Automation remains central to productivity, forecasting and operating-model discussions in finance.','Angle':'Where should a CFO automate first?','Format':'LinkedIn · Newsletter'},
]

df = pd.DataFrame(DATA)

with st.sidebar:
    st.header('Monitor settings')
    categories = st.multiselect('Categories', ['CFO','Audit','Tax','AI'], default=['CFO','Audit','Tax','AI'])
    st.markdown('**Keywords**')
    st.caption('AI agents · generative AI · AI governance · CFO · finance transformation · forecasting · ERP · audit · assurance · revision · tax · VAT · transfer pricing · e-invoicing')
    st.divider()
    st.caption('Prototype data shown in this package. Connect the weekly collector for live automated updates.')

view = df[df['Category'].isin(categories)].sort_values('Score', ascending=False)

c1,c2,c3,c4 = st.columns(4)
c1.metric('Active trends', len(view))
c2.metric('Signals analysed', int(view.Signals.sum()))
c3.metric('Source coverage', int(view.Sources.max()) if len(view) else 0)
c4.metric('Last refresh', str(date.today()))

st.subheader('🔥 Emerging trends')
for i, row in view.iterrows():
    with st.container(border=True):
        a,b,c = st.columns([5,1,1])
        a.markdown(f"### {row['Trend']}")
        a.caption(f"{row['Category']} · {row['Signals']} signals · {row['Sources']} sources")
        b.metric('Trend score', row['Score'])
        c.metric('WoW', row['WoW'])
        st.write(row['Why'])
        st.markdown(f"**Communication opportunity:** {row['Angle']}")
        st.caption(f"Suggested format: {row['Format']}")

st.subheader('Trend overview')
st.bar_chart(view.set_index('Trend')['Score'])

st.subheader('Source universe')
st.markdown('''
- **KPMG Denmark Insights** — AI & Data, Audit & Assurance, Corporate Tax, Market Trends
- **FSR – danske revisorer** — audit, accounting, tax and industry updates
- **Skattestyrelsen** — tax news and official updates
- **Digitaliseringsstyrelsen** — AI regulation, supervision and digitalisation
- Extendable with additional public RSS/API sources
''')

st.subheader('How the weekly engine works')
st.code('''1. Fetch new public articles / RSS entries\n2. Deduplicate and keyword-filter\n3. Classify: CFO / Audit / Tax / AI\n4. Extract topic + audience + communication angle\n5. Aggregate topics and compare with prior weeks\n6. Calculate trend score\n7. Publish the new dashboard snapshot''', language='text')
