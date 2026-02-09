import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64

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

# 页面导航状态
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# 数据加载函数支持CSV/Excel文件上传
@st.cache_data
def load_data(uploaded_file, file_type):
    try:
        if file_type == 'csv':
            return pd.read_csv(uploaded_file)
        elif file_type == 'excel':
            return pd.read_excel(uploaded_file)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.sidebar.warning(f"⚠️ Error loading file: {e}")
        return pd.DataFrame()

# 侧边栏添加数据上传功能
with st.sidebar.expander("📁 Upload Data", expanded=True):
    st.markdown("Upload CSV or Excel files for custom data analysis")
    st.markdown("*Note: Currently accepting any format for testing purposes*")
    st.markdown("*For internal testing only – Production will auto-load CDC/HRSA data*")
    
    # 数据文件上传
    uploaded_file = st.file_uploader("Upload Data File", type=["csv", "xlsx", "xls"])

# 加载数据
if uploaded_file:
    # 确定文件类型
    file_type = 'csv' if uploaded_file.name.endswith('.csv') else 'excel'
    
    # 加载上传的数据
    uploaded_data = load_data(uploaded_file, file_type)
    
    if not uploaded_data.empty:
        st.sidebar.success("✅ Data uploaded successfully!")
        st.sidebar.write(f"📊 Uploaded file contains {len(uploaded_data)} rows and {len(uploaded_data.columns)} columns")
        st.sidebar.write("Columns:", uploaded_data.columns.tolist())
        
        # 暂时使用上传的数据作为州级数据
        state_data = uploaded_data
        # 创建空的县级数据
        county_data = pd.DataFrame()
    else:
        st.sidebar.warning("⚠️ Failed to load data. Please check your file format.")
        state_data = pd.DataFrame()
        county_data = pd.DataFrame()
else:
    # 未上传文件时的提示
    state_data = pd.DataFrame()
    county_data = pd.DataFrame()
    st.sidebar.info("ℹ️ Please upload a data file to continue.")

# 侧边栏导航
st.sidebar.title("FemTech BI Dashboard")

# 使用session_state管理页面导航
page_options = ["Home", "Dashboard", "Gap & Opportunity", "AI Insights", "Download Center"]
selected_page = st.sidebar.radio(
    "Navigation",
    page_options,
    index=page_options.index(st.session_state.page) if st.session_state.page in page_options else 0
)

# 更新session_state中的页面
if selected_page != st.session_state.page:
    st.session_state.page = selected_page

# 使用session_state中的页面值
page = st.session_state.page

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
        
        # 应用内表单
        st.markdown("### Required Form")
        st.write("Please complete this form to access the dashboard:")
        
        with st.form("access_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            organization = st.text_input("Organization")
            purpose = st.text_area("What are you hoping to find?")
            
            submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if name and email:
                st.session_state.form_completed = True
                st.success("Thank you! You now have access to the dashboard.")
                # 重定向到仪表板
                st.session_state.page = "Dashboard"
            else:
                st.error("Please fill in at least your name and email.")
    else:
        st.success("You have access to the dashboard. Click 'Explore the Dashboard' to begin.")

# 仪表板视图
elif page == "Dashboard":
    if st.session_state.form_completed:
        if not state_data.empty:
            st.title("Deep South FemTech Decision Center")
            st.subheader("Layout 2.0 - Equity-Centered Insights")
            
            try:
                # 检查数据结构
                cols = state_data.columns.str.lower()
                has_births = 'births' in cols
                has_race = 'race' in cols or 'single race' in cols
                has_year = 'year' in cols
                has_prenatal = 'prenatal' in cols
                has_birth_rate = any('birth rate' in col for col in cols)
                has_mother_age = any('age of mother' in col for col in cols)
                
                # 找到相关列
                state_columns = [col for col in state_data.columns if 'state' in col.lower()]
                birth_col = [col for col in state_data.columns if 'birth' in col.lower() and not 'rate' in col.lower()][0] if has_births else None
                prenatal_col = [col for col in state_data.columns if 'prenatal' in col.lower()][0] if has_prenatal else None
                birth_rate_col = [col for col in state_data.columns if 'birth rate' in col.lower()][0] if has_birth_rate else None
                mother_age_col = [col for col in state_data.columns if 'age of mother' in col.lower()][0] if has_mother_age else None
                year_col = [col for col in state_data.columns if 'year' in col.lower()][0] if has_year else None
                
                # 第一区：KPI关键指标卡(Summary Cards)
                st.subheader("🎯 Key Performance Indicators")
                
                # 创建三列布局
                col1, col2, col3 = st.columns(3)
                
                # 卡片1：深南部总出生数
                if birth_col:
                    total_births = state_data[birth_col].sum()
                    col1.metric(
                        label="Total Births",
                        value=f"{total_births:,.0f}",
                        delta="Deep South Total",
                        delta_color="normal"
                    )
                else:
                    col1.metric(
                        label="Total Births",
                        value="N/A",
                        delta="Data Not Available"
                    )
                
                # 卡片2：平均产前检查次数
                if prenatal_col:
                    avg_prenatal = state_data[prenatal_col].mean()
                    col2.metric(
                        label="Avg Prenatal Visits",
                        value=f"{avg_prenatal:.1f}",
                        delta="Per Mother",
                        delta_color="normal"
                    )
                else:
                    col2.metric(
                        label="Avg Prenatal Visits",
                        value="N/A",
                        delta="Data Not Available"
                    )
                
                # 卡片3：缺口州数量
                if state_columns:
                    unique_states = state_data[state_columns[0]].nunique()
                    col3.metric(
                        label="States Covered",
                        value=f"{unique_states}",
                        delta="Deep South States",
                        delta_color="normal"
                    )
                else:
                    col3.metric(
                        label="States Covered",
                        value="N/A",
                        delta="Data Not Available"
                    )
                
                # 第二区和第三区：市场与规模 + 医疗公平性对比
                st.subheader("📊 Market & Equity Analysis")
                
                # 创建两列布局
                market_col, equity_col = st.columns(2)
                
                # 第二区：市场与规模(Market & Scale) - 中层左侧
                with market_col:
                    st.markdown("### 📈 Market & Scale")
                    
                    if state_columns and birth_col:
                        # 按州计算出生数
                        state_births = state_data.groupby(state_columns[0])[birth_col].sum().reset_index()
                        
                        # 创建饼图
                        fig_market = px.pie(
                            state_births,
                            values=birth_col,
                            names=state_columns[0],
                            title="Births by State",
                            color_discrete_sequence=["#FF7F50", "#B2AC88", "#FFA07A", "#C5D5CB"]
                        )
                        # 添加百分比标签
                        fig_market.update_traces(textinfo='percent+label')
                        # 调整为环形图
                        fig_market.update_traces(hole=0.4)
                        st.plotly_chart(fig_market, width='stretch')
                    else:
                        st.info("ℹ️ Market data not available. Please ensure your data contains State and Births columns.")
                
                # 第三区：医疗公平性对比(Equity Comparison) - 中层右侧
                with equity_col:
                    st.markdown("### ⚖️ Equity Comparison")
                    
                    if state_columns and (birth_rate_col or prenatal_col):
                        # 选择要对比的指标
                        metric_col = birth_rate_col if birth_rate_col else prenatal_col
                        metric_name = "Birth Rate" if birth_rate_col else "Prenatal Visits"
                        
                        # 按州计算平均值
                        state_metric = state_data.groupby(state_columns[0])[metric_col].mean().reset_index()
                        
                        # 创建柱状图
                        fig_equity = px.bar(
                            state_metric,
                            x=state_columns[0],
                            y=metric_col,
                            title=f"{metric_name} by State",
                            color_discrete_sequence=["#FF7F50", "#B2AC88", "#FFA07A", "#C5D5CB"],
                            barmode='group'
                        )
                        fig_equity.update_layout(bargap=0.2)
                        st.plotly_chart(fig_equity, width='stretch')
                    else:
                        st.info("ℹ️ Equity data not available. Please ensure your data contains State and Birth Rate or Prenatal Visits columns.")
                
                # 第四区：人群画像与趋势(Persons & Trends) - 底层布局
                st.subheader("👥 Personas & Trends")
                
                # 创建两列布局
                persona_col, trend_col = st.columns(2)
                
                # 左侧：母亲年龄分布[直方图]
                with persona_col:
                    st.markdown("### 📊 Mother's Age Distribution")
                    
                    if mother_age_col:
                        # 计算平均年龄
                        mean_age = state_data[mother_age_col].mean()
                        
                        # 创建直方图
                        fig_age = px.histogram(
                            state_data,
                            x=mother_age_col,
                            title="Age Distribution",
                            labels={mother_age_col: "Age (years)"},
                            color_discrete_sequence=["#FF7F50"],
                            nbins=int(state_data[mother_age_col].max() - state_data[mother_age_col].min()) + 1,
                            range_x=[state_data[mother_age_col].min() - 0.5, state_data[mother_age_col].max() + 0.5]
                        )
                        
                        # 添加白色边框
                        fig_age.update_traces(
                            marker=dict(
                                line=dict(
                                    color='white',
                                    width=1
                                )
                            )
                        )
                        
                        # 添加平均年龄辅助线
                        fig_age.add_vline(
                            x=mean_age,
                            line_dash="dash",
                            line_color="#B2AC88",
                            annotation_text=f"Mean: {mean_age:.1f}",
                            annotation_position="top right"
                        )
                        
                        # 优化坐标轴
                        fig_age.update_layout(
                            xaxis=dict(
                                tickmode='linear',
                                tick0=round(state_data[mother_age_col].min()),
                                dtick=1,
                                range=[round(state_data[mother_age_col].min()) - 0.5, round(state_data[mother_age_col].max()) + 0.5]
                            )
                        )
                        st.plotly_chart(fig_age, width='stretch')
                    else:
                        st.info("ℹ️ Age data not available. Please ensure your data contains Mother's Age column.")
                
                # 右侧：健康改善趋势[折线图]
                with trend_col:
                    st.markdown("### 📉 Health Improvement Trends")
                    
                    if year_col and prenatal_col:
                        # 按年份计算平均产前检查次数
                        year_trend = state_data.groupby(year_col)[prenatal_col].mean().reset_index()
                        
                        # 创建折线图
                        fig_trend = px.line(
                            year_trend,
                            x=year_col,
                            y=prenatal_col,
                            title="Prenatal Visits Over Time",
                            labels={prenatal_col: "Avg. Visits", year_col: "Year"},
                            color_discrete_sequence=["#B2AC88"]
                        )
                        # 添加标记点
                        fig_trend.update_traces(mode='lines+markers', marker=dict(size=8))
                        st.plotly_chart(fig_trend, width='stretch')
                    else:
                        st.info("ℹ️ Trend data not available. Please ensure your data contains Year and Prenatal Visits columns.")
                
                # 数据概览（可选）
                with st.expander("📋 Data Overview"):
                    st.write(f"Uploaded file contains {len(state_data)} rows and {len(state_data.columns)} columns")
                    st.write("Sample Data:")
                    st.dataframe(state_data.head())
                    
            except Exception as e:
                st.warning(f"⚠️ Error analyzing data structure. Please ensure your data contains State, Year, Births columns and try again. Error: {e}")
                st.info("ℹ️ Basic data view only available. Detailed analysis will be implemented once data structure is finalized.")
        else:
            st.info("ℹ️ No data available. Please upload a data file in the sidebar.")
    else:
        st.warning("Please complete the form on the Home page before accessing the dashboard.")
        if st.button("Go to Home page"):
            st.session_state.page = "Home"

# 差距与机会层
elif page == "Gap & Opportunity":
    st.title("Gap & Opportunity Analysis")
    st.info("This section will display high-need, low-innovation counties using HRSA + Census + FemTech startup data.")
    st.warning("⚠️ Data not yet loaded. Coming in Phase 2 after CDC data validation.")
    
    # 显示占位示意图描述
    st.subheader("Planned Features:")
    st.markdown("""
    - **High-need, low-innovation county identification**
    - **Interactive filters** (State, race, age, health condition)
    - **Opportunity zone visualization** on map
    - **Detailed gap analysis** with actionable insights
    """)
    
    # 显示示例数据结构
    st.subheader("Expected Data Structure:")
    sample_data = pd.DataFrame({
        "County": ["Example County 1", "Example County 2", "Example County 3"],
        "State": ["Georgia", "Alabama", "Mississippi"],
        "Need Score": [85, 90, 95],
        "Innovation Score": [20, 15, 10]
    })
    st.dataframe(sample_data)
    
    st.info("Data integration with HRSA's HPSA dataset coming soon!")

# AI洞察页面
elif page == "AI Insights":
    st.title("AI-Powered Insights")
    st.markdown("Ask a question about Deep South women's health data")
    
    # Q&A框
    user_query = st.text_input(
        "e.g., 'Where is Black maternal mortality highest in Alabama?'", 
        key="ai_query"
    )
    
    if user_query:
        with st.spinner("Generating insight..."):
            # 模拟AI响应
            response = """
            Based on CDC 2024 data, in Alabama, Black women have the highest maternal mortality rate (XX/100k), concentrated in counties like [X], [Y]. 
            Key drivers include low prenatal visit rates (avg. """
            
            # 尝试从数据中获取一些真实值
            try:
                if not state_data.empty:
                    # 检查是否有产前检查数据
                    prenatal_cols = [col for col in state_data.columns if 'prenatal' in col.lower()]
                    if prenatal_cols:
                        avg_prenatal = state_data[prenatal_cols[0]].mean()
                        response += f"{avg_prenatal:.1f}"
                    else:
                        response += "9.2"
                else:
                    response += "9.2"
            except Exception:
                response += "9.2"
            
            response += "\n\n**Recommended Action:** Increase funding for prenatal care programs in rural and underserved areas, with targeted outreach to Black and Indigenous women."
            
            st.info(response)
    
    # 示例问题
    st.subheader("Example Queries:")
    st.markdown("""
    - "Where is Black maternal mortality highest in Alabama?"
    - "Which counties have the greatest need for FemTech innovation?"
    - "What are the top investment opportunities in the Deep South?"
    - "How has prenatal care access changed over time across racial groups?"
    """)
    
    # 数据驱动洞察
    if not state_data.empty:
        st.subheader("📊 Data-Driven Insights")
        
        # 基本统计洞察
        try:
            # 找到数值列
            numeric_cols = state_data.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                st.write("**Key Statistics from Uploaded Data:**")
                for col in numeric_cols[:3]:  # 只显示前3个
                    mean_val = state_data[col].mean()
                    min_val = state_data[col].min()
                    max_val = state_data[col].max()
                    st.write(f"- {col}: Mean = {mean_val:.2f}, Range = {min_val:.2f} - {max_val:.2f}")
        except Exception as e:
            st.warning(f"⚠️ Could not generate data insights: {e}")

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