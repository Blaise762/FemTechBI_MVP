import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
import io

# 页面配置
st.set_page_config(
    page_title="FemTech BI Dashboard - Deep South",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 表单捕获功能 - 外部表单重定向
if 'form_completed' not in st.session_state:
    st.session_state.form_completed = False

# 模拟数据 - 将在后续替换为真实数据
@st.cache_data
def load_sample_data():
    # 模拟州级数据
    state_data = pd.DataFrame({
        "State": ["Georgia", "Florida", "Alabama", "Mississippi", "Louisiana", "South Carolina"],
        "State Abbr": ["GA", "FL", "AL", "MS", "LA", "SC"],
        "Maternal Mortality Rate": [30.8, 27.6, 47.9, 65.7, 45.9, 32.5],
        "OB-GYN Density": [45.2, 52.1, 31.5, 28.9, 35.7, 41.3],
        "FemTech Startups": [25, 32, 8, 5, 12, 15],
        "Black Women Population %": [31.0, 16.9, 26.8, 37.8, 32.0, 27.6],
        "Rural Population %": [25.1, 17.8, 41.3, 52.1, 44.0, 31.2]
    })
    
    # 模拟县级差距数据
    county_data = pd.DataFrame({
        "State": ["Georgia", "Georgia", "Florida", "Florida", "Alabama", "Alabama", "Mississippi", "Mississippi", "Louisiana", "Louisiana", "South Carolina", "South Carolina"],
        "County": ["Fulton", "Rural County", "Miami-Dade", "Rural County", "Jefferson", "Rural County", "Hinds", "Rural County", "Orleans", "Rural County", "Charleston", "Rural County"],
        "Need Score": [30, 85, 35, 75, 40, 90, 45, 95, 38, 88, 32, 80],
        "Innovation Score": [90, 20, 85, 25, 70, 15, 65, 10, 75, 18, 80, 22]
    })
    
    return state_data, county_data

# 加载数据
state_data, county_data = load_sample_data()

# 侧边栏导航
st.sidebar.title("FemTech BI Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Dashboard", "Gap & Opportunity", "AI Insights", "Download Center"]
)

# 首页
if page == "Home":
    st.title("FemTech BI Dashboard - Deep South")
    st.subheader("Equity-Centered Insights for Women's Health Innovation")
    
    # Hero区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Our Vision
        We are building a regionally focused, equity-centered FemTech Business Intelligence platform that tracks data and insights across six Deep South states (GA, FL, AL, MS, LA, SC).
        
        ### Who We Serve
        - **Founders** (seeking opportunity zones, data-backed strategy)
        - **Funders** (impact investors, grantmakers, VCs)
        - **Systems** (health orgs, policymakers, accelerators)
        """)
        
        # CTA按钮
        st.markdown("""
        <style>
        .stButton > button {
            width: 200px;
            margin: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col_cta1, col_cta2, col_cta3 = st.columns(3)
        with col_cta1:
            if st.button("Explore the Dashboard"):
                if st.session_state.form_completed:
                    st.session_state.page = "Dashboard"
                else:
                    st.warning("Please complete the form before accessing the dashboard.")
        with col_cta2:
            if st.button("Download Snapshot"):
                st.session_state.page = "Download Center"
        with col_cta3:
            if st.button("Request Custom Insights"):
                st.session_state.page = "Download Center"
    
    with col2:
        st.markdown("### Deep South States")
        # 显示六个州的列表和地图描述
        st.markdown("""
        - Georgia (GA)
        - Florida (FL)
        - Alabama (AL)
        - Mississippi (MS)
        - Louisiana (LA)
        - South Carolina (SC)
        """)
        st.info("Interactive map visualization coming soon!")
    
    # 表单捕获功能
    st.markdown("""
    ---
    ### Access the Dashboard
    """
    )
    
    if not st.session_state.form_completed:
        st.warning("Please complete the form below to access the full dashboard.")
        
        # 外部表单链接
        st.markdown("""
        ### Required Form
        Please complete this form before accessing the dashboard:
        
        [Complete Form Here](https://tally.so/r/n9Xv3r) - This link will open in a new tab
        
        After submitting, return to this page and click the button below to confirm access.
        """, unsafe_allow_html=True)
        
        if st.button("I've completed the form"):
            st.session_state.form_completed = True
            st.success("Thank you! You now have access to the dashboard.")
            # 重定向到仪表板
            st.session_state.page = "Dashboard"
    else:
        st.success("You have access to the dashboard. Click 'Explore the Dashboard' to begin.")

# 仪表板视图
elif page == "Dashboard":
    if st.session_state.form_completed:
        st.title("State-by-State Dashboard")
        
        # 州选择器
        selected_state = st.selectbox("Select a State", state_data["State"].unique())
        
        # 获取所选州的数据
        state_info = state_data[state_data["State"] == selected_state].iloc[0]
        
        # 显示关键指标
        st.subheader(f"Key Metrics for {selected_state}")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Maternal Mortality Rate", f"{state_info['Maternal Mortality Rate']} per 100,000")
        with col2:
            st.metric("OB-GYN Density", f"{state_info['OB-GYN Density']} per 100,000")
        with col3:
            st.metric("FemTech Startups", state_info['FemTech Startups'])
        with col4:
            st.metric("Black Women Population", f"{state_info['Black Women Population %']}%")
        
        # 图表
        st.subheader("Data Visualizations")
        
        # 1. 州际比较 - 孕产妇死亡率
        fig1 = px.bar(
            state_data, 
            x="State", 
            y="Maternal Mortality Rate",
            title="Maternal Mortality Rate by State",
            color="Maternal Mortality Rate",
            color_continuous_scale="RdYlBu_r"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. 州际比较 - FemTech初创公司
        fig2 = px.bar(
            state_data, 
            x="State", 
            y="FemTech Startups",
            title="FemTech Startup Presence by State",
            color="FemTech Startups",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. 农村人口与OB-GYN密度关系
        fig3 = px.scatter(
            state_data, 
            x="Rural Population %", 
            y="OB-GYN Density",
            size="Maternal Mortality Rate",
            color="State",
            title="Rural Population vs OB-GYN Density",
            hover_name="State"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # 摘要框
        st.subheader("State Summary")
        st.info(f"""
        **{selected_state} Overview:**
        - Maternal mortality rate is {state_info['Maternal Mortality Rate']} per 100,000 births, which is {'above' if state_info['Maternal Mortality Rate'] > 30 else 'below'} the national average.
        - OB-GYN density is {state_info['OB-GYN Density']} per 100,000 population, indicating {'adequate' if state_info['OB-GYN Density'] > 40 else 'limited'} access to reproductive healthcare.
        - There are {state_info['FemTech Startups']} FemTech startups in the state, showing {'strong' if state_info['FemTech Startups'] > 15 else 'emerging'} innovation activity.
        - Black women make up {state_info['Black Women Population %']}% of the population, highlighting the importance of equity-centered approaches.
        - {state_info['Rural Population %']}% of the population lives in rural areas, where healthcare access is often more limited.
        """)
    else:
        st.warning("Please complete the form on the Home page before accessing the dashboard.")
        if st.button("Go to Home page"):
            st.session_state.page = "Home"

# 差距与机会层
elif page == "Gap & Opportunity":
    st.title("Gap & Opportunity Analysis")
    
    # 过滤器
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_state_gap = st.selectbox("State", ["All"] + list(state_data["State"].unique()))
    with col2:
        selected_demographic = st.selectbox("Demographic Focus", ["All", "Black Women", "Rural Communities", "Urban Communities"])
    with col3:
        selected_health_condition = st.selectbox("Health Condition", ["All", "Maternal Health", "Reproductive Health", "Primary Care"])
    
    # 筛选数据
    filtered_county_data = county_data.copy()
    if selected_state_gap != "All":
        filtered_county_data = filtered_county_data[filtered_county_data["State"] == selected_state_gap]
    
    # 高需求低创新县分析
    high_need_low_innovation = filtered_county_data[
        (filtered_county_data["Need Score"] > 70) & (filtered_county_data["Innovation Score"] < 30)
    ]
    
    # 显示结果
    st.subheader("High-Need, Low-Innovation Areas")
    
    if not high_need_low_innovation.empty:
        st.write(f"Found {len(high_need_low_innovation)} high-need, low-innovation counties:")
        st.dataframe(high_need_low_innovation)
    else:
        st.info("No high-need, low-innovation counties found with current filters.")
    
    # 可视化
    fig = px.scatter(
        filtered_county_data, 
        x="Innovation Score", 
        y="Need Score",
        color="State",
        size=[30] * len(filtered_county_data),
        hover_name="County",
        title="Need vs Innovation Score by County",
        labels={"Innovation Score": "Innovation Score (Higher = Better)", "Need Score": "Need Score (Higher = Greater Need)"}
    )
    
    # 添加参考线
    fig.add_shape(
        type="line",
        x0=30, y0=0,
        x1=30, y1=100,
        line=dict(color="Red", width=2, dash="dash")
    )
    
    fig.add_shape(
        type="line",
        x0=0, y0=70,
        x1=100, y1=70,
        line=dict(color="Red", width=2, dash="dash")
    )
    
    fig.add_annotation(
        x=15, y=85,
        text="Opportunity Zones",
        showarrow=True,
        arrowhead=2
    )
    
    st.plotly_chart(fig, use_container_width=True)

# AI洞察页面
elif page == "AI Insights":
    st.title("AI-Powered Insights")
    
    st.info("""
    **Coming Soon: Smart Insight Generator!**
    
    This feature will use GPT to generate data-driven insights and recommendations based on the dashboard data.
    
    Example queries:
    - "Where is Black maternal mortality highest in Alabama?"
    - "Which counties have the greatest need for FemTech innovation?"
    - "What are the top investment opportunities in the Deep South?"
    """)

# 下载中心
elif page == "Download Center":
    st.title("Download Center")
    
    st.subheader("Deep South FemTech Snapshot")
    st.write("Download our comprehensive snapshot of FemTech innovation and health equity in the Deep South.")
    
    # 模拟PDF下载
    def create_download_link(val, filename):
        b64 = base64.b64encode(val).decode()  # val is bytes
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download {filename}</a>'
    
    # 创建模拟PDF内容
    pdf_content = b"Simulated PDF content for Deep South FemTech Snapshot"
    
    # 添加下载按钮
    st.markdown(create_download_link(pdf_content, "Deep_South_FemTech_Snapshot.pdf"), unsafe_allow_html=True)
    
    st.subheader("Contact Us")
    
    # 联系表单
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        organization = st.text_input("Organization")
        message = st.text_area("Message")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button:
        st.success("Thank you for your message! We'll get back to you soon.")
    
    st.subheader("Stay Updated")
    st.write("Subscribe to our newsletter for the latest FemTech insights and opportunities.")
    
    # 邮件订阅
    with st.form("email_subscribe"):
        email_sub = st.text_input("Your Email")
        subscribe_button = st.form_submit_button("Subscribe")
    
    if subscribe_button:
        st.success("Thank you for subscribing!")

# 页脚
st.markdown("""
---
### Footer
*Demo only – not for redistribution.*
*FemTech BI Dashboard for the Deep South* 
""", unsafe_allow_html=True)
