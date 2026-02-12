import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import numpy as np

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
            # 尝试不同的编码格式读取CSV文件
            encodings = ['utf-8', 'latin1', 'gbk', 'gb2312']
            for encoding in encodings:
                try:
                    return pd.read_csv(uploaded_file, encoding=encoding)
                except UnicodeDecodeError:
                    uploaded_file.seek(0)  # 重置文件指针
                    continue
            # 如果所有编码都失败，使用errors='replace'
            uploaded_file.seek(0)  # 重置文件指针
            return pd.read_csv(uploaded_file, encoding='utf-8', errors='replace')
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
    
    # 双文件上传
    cdc_file = st.file_uploader("Upload CDC Data File", type=["csv", "xlsx", "xls"])
    hrsa_file = st.file_uploader("Upload HRSA Data File", type=["csv", "xlsx", "xls"])
    
    # 深南部6州过滤器
    st.markdown("\n**Deep South States Filter**")
    selected_states = st.multiselect(
        "Select states to analyze",
        options=["AL", "FL", "GA", "LA", "MS", "SC"],
        default=["AL", "FL", "GA", "LA", "MS", "SC"]
    )

# 加载数据
cdc_data = pd.DataFrame()
hrsa_data = pd.DataFrame()
merged_data = pd.DataFrame()

# 加载CDC数据
if cdc_file:
    cdc_file_type = 'csv' if cdc_file.name.endswith('.csv') else 'excel'
    cdc_data = load_data(cdc_file, cdc_file_type)
    if not cdc_data.empty:
        st.sidebar.success("✅ CDC Data uploaded successfully!")
        st.sidebar.write(f"📊 CDC file: {len(cdc_data)} rows, {len(cdc_data.columns)} columns")
    else:
        st.sidebar.warning("⚠️ Failed to load CDC data. Please check your file format.")

# 加载HRSA数据
if hrsa_file:
    hrsa_file_type = 'csv' if hrsa_file.name.endswith('.csv') else 'excel'
    hrsa_data = load_data(hrsa_file, hrsa_file_type)
    if not hrsa_data.empty:
        st.sidebar.success("✅ HRSA Data uploaded successfully!")
        st.sidebar.write(f"📊 HRSA file: {len(hrsa_data)} rows, {len(hrsa_data.columns)} columns")
    else:
        st.sidebar.warning("⚠️ Failed to load HRSA data. Please check your file format.")

# 检查是否有数据
if cdc_data.empty and hrsa_data.empty:
    st.sidebar.info("ℹ️ Please upload both CDC and HRSA data files to continue.")
else:
    st.sidebar.info("ℹ️ Data ready for analysis.")

# 州名映射字典：全称 -> 简称（仅深南部6州）
STATE_MAPPING = {
    'Alabama': 'AL',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Louisiana': 'LA',
    'Mississippi': 'MS',
    'South Carolina': 'SC'
}

# 标准化州名函数
def standardize_state_name(state_name):
    """将州名标准化为简称"""
    if pd.isna(state_name):
        return state_name
    
    # 转换为字符串并去除空格
    state_str = str(state_name).strip()
    
    # 如果已经是简称（2个字符），直接返回
    if len(state_str) == 2 and state_str.isalpha():
        return state_str.upper()
    
    # 尝试从全称映射到简称
    for full_name, abbreviation in STATE_MAPPING.items():
        if full_name.lower() == state_str.lower():
            return abbreviation
    
    # 如果无法映射，返回原始值
    return state_str

# 辅助函数：将值转换为数值类型
def to_numeric(value):
    """将字符串或其他类型的值转换为数值类型"""
    if pd.isna(value):
        return np.nan
    
    try:
        # 转换为字符串
        str_val = str(value)
        # 去除千分位逗号
        str_val = str_val.replace(',', '')
        # 转换为浮点数
        return float(str_val)
    except (ValueError, TypeError):
        # 如果转换失败，返回np.nan
        return np.nan

# 数据清理与字段映射函数
def clean_and_map_cdc_data(df):
    """清理并映射CDC数据字段"""
    if df.empty:
        return df
    
    # 创建映射后的DataFrame
    mapped_df = pd.DataFrame()
    
    # 标准化列名（转为小写并去除空格）
    df.columns = df.columns.str.lower().str.strip()
    
    # 映射Births字段
    birth_cols = [col for col in df.columns if 'birth' in col and not 'rate' in col]
    if birth_cols:
        # 应用数值转换，处理千分位逗号
        mapped_df['total_births'] = df[birth_cols[0]].apply(to_numeric)
    
    # 映射Prenatal Visits字段
    prenatal_cols = [col for col in df.columns if 'prenatal' in col or 'visit' in col]
    if prenatal_cols:
        # 应用数值转换
        mapped_df['prenatal_visits'] = df[prenatal_cols[0]].apply(to_numeric)
    
    # 映射State字段
    state_cols = [col for col in df.columns if 'state' in col]
    if state_cols:
        # 标准化州名为简称
        mapped_df['state'] = df[state_cols[0]].apply(standardize_state_name)
    
    # 映射Year字段
    year_cols = [col for col in df.columns if 'year' in col]
    if year_cols:
        # 应用数值转换
        mapped_df['year'] = df[year_cols[0]].apply(to_numeric)
    
    # 映射母亲年龄字段
    age_cols = [col for col in df.columns if 'age' in col and 'mother' in col]
    if not age_cols:
        # 尝试更广泛的匹配
        age_cols = [col for col in df.columns if 'age' in col]
    if age_cols:
        # 应用数值转换
        mapped_df['mother_age'] = df[age_cols[0]].apply(to_numeric)
    
    # 映射Race字段
    race_cols = [col for col in df.columns if 'race' in col]
    if race_cols:
        mapped_df['race'] = df[race_cols[0]]
    
    return mapped_df

def clean_and_map_hrsa_data(df):
    """清理并映射HRSA数据字段"""
    if df.empty:
        return df
    
    # 创建映射后的DataFrame
    mapped_df = pd.DataFrame()
    
    # 标准化列名（转为小写并去除空格）
    df.columns = df.columns.str.lower().str.strip()
    
    # 映射HPSA Score字段
    hpsa_cols = [col for col in df.columns if 'hpsa' in col and 'score' in col]
    if hpsa_cols:
        # 应用数值转换，处理混合数据类型
        mapped_df['gap_score'] = df[hpsa_cols[0]].apply(to_numeric)
    
    # 映射State字段
    state_cols = [col for col in df.columns if 'state' in col]
    if state_cols:
        # 标准化州名为简称
        mapped_df['state'] = df[state_cols[0]].apply(standardize_state_name)
    
    return mapped_df

# 清理并映射数据
mapped_cdc = clean_and_map_cdc_data(cdc_data)
mapped_hrsa = clean_and_map_hrsa_data(hrsa_data)

# 执行数据关联
def merge_data(cdc_df, hrsa_df):
    """关联CDC和HRSA数据"""
    if cdc_df.empty or hrsa_df.empty:
        return pd.DataFrame()
    
    # 确定连接键
    has_state = 'state' in cdc_df.columns and 'state' in hrsa_df.columns
    
    if has_state:
        # 先聚合，再合并（避免笛卡尔积）
        # 1. 对CDC数据按州和年份聚合（保留年份维度）
        # 聚合所有必要的列
        cdc_agg = cdc_df.groupby(['state', 'year']).agg({
            'total_births': 'sum',  # 总出生数
            'prenatal_visits': 'mean',  # 平均产前检查次数
            'mother_age': 'mean'  # 平均母亲年龄
        }).reset_index()
        
        # 2. 对HRSA数据按州聚合（计算州级平均缺口分数）
        hrsa_agg = hrsa_df.groupby('state').agg({
            'gap_score': 'mean'  # 或'max'/'sum'，根据业务需求选择
        }).reset_index()
        
        # 3. 再按州合并
        merged = pd.merge(
            cdc_agg, 
            hrsa_agg, 
            on=['state'], 
            how='left'
        )
    else:
        # 没有共同的连接键，返回空数据框
        st.sidebar.warning("⚠️ No common merge keys found. Please ensure both files have State columns.")
        return pd.DataFrame()
    
    # 填充缺失值：如果某个州在CDC有数据但在HRSA没数据，HPSA Score设为0
    if 'gap_score' in merged.columns:
        merged['gap_score'] = merged['gap_score'].fillna(0)
    
    return merged

# 执行数据关联
merged_data = merge_data(mapped_cdc, mapped_hrsa)

# 应用深南部州过滤器
if not merged_data.empty and selected_states:
    merged_data = merged_data[merged_data['state'].isin(selected_states)]

# 暂时使用数据变量
state_data = mapped_cdc  # 暂时使用映射后的CDC数据作为州级数据


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
    st.rerun()

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
                    st.rerun()
                else:
                    st.warning("Please complete the form before accessing the dashboard.")
        with col_cta2:
            if st.button("Download Snapshot"):
                st.session_state.page = "Download Center"
                st.rerun()
        with col_cta3:
            if st.button("Request Custom Insights"):
                st.session_state.page = "Download Center"
                st.rerun()
    
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
        if not merged_data.empty:
            st.title("Deep South FemTech Decision Center")
            st.subheader("Layout 2.0 - Equity-Centered Insights")
            
            try:
                # 第一区：KPI关键指标卡(Summary Cards)
                st.subheader("🎯 Key Performance Indicators")
                
                # 创建三列布局
                col1, col2, col3 = st.columns(3)
                
                # 卡片1：总市场规模 → 关联表中Births的总和
                if 'total_births' in merged_data.columns:
                    total_births = merged_data['total_births'].sum()
                    col1.metric(
                        label="Total Market Size",
                        value=f"{total_births:,.0f}",
                        delta="Total Births",
                        delta_color="normal"
                    )
                else:
                    col1.metric(
                        label="Total Market Size",
                        value="N/A",
                        delta="Data Not Available"
                    )
                
                # 卡片2：平均缺口严重度 → HPSA Score的平均值
                if 'gap_score' in merged_data.columns:
                    avg_gap_score = merged_data['gap_score'].mean()
                    col2.metric(
                        label="Avg Gap Severity",
                        value=f"{avg_gap_score:.2f}",
                        delta="HPSA Score Avg",
                        delta_color="normal"
                    )
                else:
                    col2.metric(
                        label="Avg Gap Severity",
                        value="N/A",
                        delta="Data Not Available"
                    )
                
                # 卡片3：覆盖州数量
                if 'state' in merged_data.columns:
                    unique_states = merged_data['state'].nunique()
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
                    
                    if 'state' in merged_data.columns and 'total_births' in merged_data.columns:
                        # 按州计算出生数
                        state_births = merged_data.groupby('state')['total_births'].sum().reset_index()
                        
                        # 确保state列是字符串类型
                        state_births['state'] = state_births['state'].astype(str)
                        
                        # 创建饼图
                        fig_market = px.pie(
                            state_births,
                            values='total_births',
                            names='state',
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
                    
                    if 'state' in merged_data.columns:
                        # 选择要对比的指标
                        if 'gap_score' in merged_data.columns:
                            metric_col = 'gap_score'
                            metric_name = "Gap Severity"
                        elif 'prenatal_visits' in merged_data.columns:
                            metric_col = 'prenatal_visits'
                            metric_name = "Prenatal Visits"
                        else:
                            metric_col = None
                            metric_name = "No Data"
                        
                        if metric_col:
                            # 按州计算平均值
                            state_metric = merged_data.groupby('state')[metric_col].mean().reset_index()
                            
                            # 确保state列是字符串类型
                            state_metric['state'] = state_metric['state'].astype(str)
                            
                            # 创建柱状图
                            fig_equity = px.bar(
                                state_metric,
                                x='state',
                                y=metric_col,
                                title=f"{metric_name} by State",
                                color_discrete_sequence=["#FF7F50", "#B2AC88", "#FFA07A", "#C5D5CB"],
                                barmode='group'
                            )
                            fig_equity.update_layout(bargap=0.2)
                            st.plotly_chart(fig_equity, width='stretch')
                        else:
                            st.info("ℹ️ Equity data not available. Please ensure your data contains Gap Score or Prenatal Visits columns.")
                    else:
                        st.info("ℹ️ Equity data not available. Please ensure your data contains State column.")
                
                # 第四区：人群画像与趋势(Persons & Trends) - 底层布局
                st.subheader("👥 Personas & Trends")
                
                # 创建两列布局
                persona_col, trend_col = st.columns(2)
                
                # 左侧：母亲年龄分布[直方图]
                with persona_col:
                    st.markdown("### 📊 Mother's Age Distribution")
                    
                    # 检查是否有母亲年龄数据，使用merged_data确保数据一致性
                    if not merged_data.empty and 'mother_age' in merged_data.columns:
                        # 过滤掉年龄为0或无效的值
                        age_data = merged_data[merged_data['mother_age'] > 0].copy()
                        
                        if not age_data.empty:
                            # 创建直方图
                            fig_age = px.histogram(
                                age_data,
                                x='mother_age',
                                title="Distribution of Mother's Average Age",
                                labels={'mother_age': 'Average Age of Mother (years)', 'count': 'Frequency'},
                                color_discrete_sequence=["#FF7F50", "#B2AC88", "#FFA07A", "#C5D5CB"],
                                nbins=15
                            )
                            # 添加柱边框
                            fig_age.update_traces(marker=dict(line=dict(color='#000000', width=1)))
                            # 添加均值辅助线
                            mean_age = age_data['mother_age'].mean()
                            fig_age.add_vline(x=mean_age, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_age:.2f}")
                            # 调整布局
                            fig_age.update_layout(bargap=0.1)
                            st.plotly_chart(fig_age, use_container_width=True)
                        else:
                            st.info("ℹ️ No valid age data available. Please ensure your CDC data contains non-zero age values.")
                    else:
                        st.info("ℹ️ Age distribution data not available in current dataset. Please upload CDC data with mother's age information.")
                
                # 右侧：健康改善趋势[折线图]
                with trend_col:
                    st.markdown("### 📉 Health Improvement Trends")
                    
                    # 使用merged_data确保数据一致性
                    if 'year' in merged_data.columns and 'prenatal_visits' in merged_data.columns:
                        # 过滤年份为0或空的值
                        trend_df = merged_data[(merged_data['year'] > 0) & (merged_data['year'] < 3000)].copy()
                        
                        # 检查数据量
                        if len(trend_df) > 0:
                            # 按年份计算平均产前检查次数
                            year_trend = trend_df.groupby('year')['prenatal_visits'].mean().reset_index()
                            
                            if not year_trend.empty:
                                # 确保至少有一个数据点，强制显示折线图
                                fig_trend = px.line(
                                    year_trend,
                                    x='year',
                                    y='prenatal_visits',
                                    title="Avg Prenatal Visits Over Time (Based on Original Annual Data)",
                                    labels={'prenatal_visits': "Avg. Visits", 'year': "Year"},
                                    color_discrete_sequence=["#B2AC88"]
                                )
                                # 控制X轴只显示年份区间
                                fig_trend.update_layout(
                                    xaxis=dict(
                                        tickmode='linear',
                                        dtick=1
                                    )
                                )
                                # 添加标记点
                                fig_trend.update_traces(mode='lines+markers', marker=dict(size=8))
                                st.plotly_chart(fig_trend, use_container_width=True)
                            else:
                                st.info("ℹ️ Trend data unavailable.")
                        else:
                            st.info("ℹ️ Trend data unavailable.")
                    else:
                        st.info("ℹ️ Trend data not available. Please ensure your data contains Year and Prenatal Visits columns.")
                
                # 数据概览（可选）
                with st.expander("📋 Data Overview"):
                    st.write(f"Merged data contains {len(merged_data)} rows and {len(merged_data.columns)} columns")
                    st.write("Sample Data:")
                    st.dataframe(merged_data.head())
                    
            except Exception as e:
                st.warning(f"⚠️ Error analyzing data structure. Please ensure your data contains State and relevant metric columns. Error: {e}")
                st.info("ℹ️ Basic data view only available. Detailed analysis will be implemented once data structure is finalized.")
        else:
            st.info("ℹ️ No merged data available. Please upload both CDC and HRSA data files in the sidebar.")
    else:
        st.warning("Please complete the form on the Home page before accessing the dashboard.")
        if st.button("Go to Home page"):
            st.session_state.page = "Home"
            st.rerun()

# 差距与机会层
elif page == "Gap & Opportunity":
    st.title("Gap & Opportunity Analysis")
    
    if not merged_data.empty:
        # 计算Opportunity指数
        if 'total_births' in merged_data.columns and 'gap_score' in merged_data.columns:
            # 先按州聚合核心指标
            state_aggregated = merged_data.groupby('state').agg({
                'total_births': 'sum',      # 计算每个州的总出生数
                'gap_score': 'mean'         # 计算每个州的平均缺口分数
            }).reset_index()
            
            # 计算所有州的最大总出生数
            max_births = state_aggregated['total_births'].max() if not state_aggregated['total_births'].empty else 1
            
            # 用聚合后的指标重新计算州级机会指数
            state_aggregated['opportunity_index'] = (state_aggregated['total_births'] / max_births) * state_aggregated['gap_score']
            
            # 显示机会指数最高的前10个州
            top_opportunities = state_aggregated.nlargest(10, 'opportunity_index')[['state', 'total_births', 'gap_score', 'opportunity_index']]
            
            st.subheader("🎯 Top Opportunity Zones")
            st.dataframe(top_opportunities.style.format({
                'total_births': '{:,.0f}',
                'gap_score': '{:.2f}',
                'opportunity_index': '{:.2f}'
            }))
            
            # 创建机会指数可视化
            st.subheader("📊 Opportunity Analysis")
            
            # 创建两列布局
            viz_col1, viz_col2 = st.columns(2)
            
            # 使用之前已经计算好的state_aggregated数据
            # 不需要重新聚合，因为我们已经在前面计算了正确的州级机会指数
            
            # 筛选机会指数前20%的区域
            threshold = state_aggregated['opportunity_index'].quantile(0.8)
            high_opportunity = state_aggregated[state_aggregated['opportunity_index'] >= threshold]
            
            # 左侧：散点图（气泡图）
            with viz_col1:
                st.markdown("### 🔍 Opportunity Heatmap")
                # 准备hover数据
                hover_data = ['state']
                
                # 创建散点图，使用聚合后的数据
                fig_scatter = px.scatter(
                    state_aggregated,
                    x='total_births',
                    y='gap_score',
                    size='opportunity_index',
                    color='opportunity_index',
                    hover_data=hover_data,
                    title='Opportunity Zones: Births vs Gap Score',
                    color_continuous_scale=["#B2AC88", "#FF7F50"]
                )
                
                # 对高机会点添加标签
                for i, row in high_opportunity.iterrows():
                    fig_scatter.add_annotation(
                        x=row['total_births'],
                        y=row['gap_score'],
                        text=row['state'],
                        showarrow=True,
                        arrowhead=1,
                        bgcolor="white",
                        bordercolor="#FF7F50",
                        borderwidth=2
                    )
                
                fig_scatter.update_layout(
                    xaxis_title='Total Births',
                    yaxis_title='Gap Score (HPSA)',
                    width=500,
                    height=400
                )
                st.plotly_chart(fig_scatter, width='stretch')
            
            # 右侧：机会指数分布
            with viz_col2:
                st.markdown("### 📈 Opportunity Index Distribution")
                
                # 创建直方图，使用聚合后的数据
                # 使用分位数分箱，让分布更清晰
                fig_hist = px.histogram(
                    state_aggregated,
                    x='opportunity_index',
                    title='Opportunity Index Distribution',
                    color_discrete_sequence=["#FF7F50"],
                    nbins=10
                )
                
                # 修改Y轴标签为'Count of Regions'
                fig_hist.update_layout(
                    xaxis_title='Opportunity Index',
                    yaxis_title='Count of Regions',
                    width=500,
                    height=400
                )
                
                # 添加中位数和90分位数参考线
                median_value = state_aggregated['opportunity_index'].median()
                percentile_90 = state_aggregated['opportunity_index'].quantile(0.9)
                
                fig_hist.add_vline(x=median_value, line_dash="dash", line_color="green", 
                                  annotation_text=f"Median: {median_value:.2f}")
                fig_hist.add_vline(x=percentile_90, line_dash="dot", line_color="red", 
                                  annotation_text=f"90th%: {percentile_90:.2f}")
                
                st.plotly_chart(fig_hist, width='stretch')
            
            # 按州分析机会
            st.subheader("🌍 State-Level Opportunity Analysis")
            # 使用已经聚合好的state_aggregated数据
            state_opportunity = state_aggregated.copy()
            state_opportunity = state_opportunity.sort_values('opportunity_index', ascending=False)
            
            fig_state = px.bar(
                state_opportunity,
                x='state',
                y='opportunity_index',
                title='Opportunity Index by State',
                color_discrete_sequence=["#FF7F50"]
            )
            fig_state.update_layout(
                xaxis_title='State',
                yaxis_title='Average Opportunity Index'
            )
            st.plotly_chart(fig_state, width='stretch')
            
        else:
            st.warning("⚠️ Required data columns not available. Please ensure your data contains total_births and gap_score columns.")
    else:
        st.info("ℹ️ No merged data available. Please upload both CDC and HRSA data files in the sidebar.")

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
            # 基于实际数据生成响应
            response = ""
            
            # 尝试从合并数据中获取真实值
            try:
                if not merged_data.empty:
                    # 查找HPSA Score最高且Births最大的州
                    if 'gap_score' in merged_data.columns and 'total_births' in merged_data.columns:
                        # 计算综合得分（HPSA Score * Births）
                        merged_data['composite_score'] = merged_data['gap_score'] * merged_data['total_births']
                        
                        # 按州计算平均综合得分
                        state_scores = merged_data.groupby('state')['composite_score'].mean().reset_index()
                        # 找到综合得分最高的州
                        top_state = state_scores.nlargest(1, 'composite_score').iloc[0]
                        
                        # 获取该州的详细数据
                        state_data = merged_data[merged_data['state'] == top_state['state']].iloc[0]
                        
                        # 构建响应
                        response = f"""
                        Based on the latest CDC and HRSA data, the state with the most significant healthcare gap is {top_state['state']}.
                        
                        **Key Insights:**
                        - HPSA Score: {state_data['gap_score']:.2f} (higher scores indicate greater need)
                        - Total Births: {state_data['total_births']:,.0f} (represents market size)
                        
                        **Recommended Action:** In {top_state['state']}, healthcare gap is most significant. We recommend prioritizing FemTech innovation and investment in this state, with targeted programs to improve prenatal care access and maternal health outcomes.
                        """
                    else:
                        response = """
                        Based on available data, we can provide insights about women's health in the Deep South.
                        
                        **Recommended Action:** Increase funding for prenatal care programs in rural and underserved areas, with targeted outreach to Black and Indigenous women.
                        """
                else:
                    response = """
                    Based on CDC 2024 data, in Alabama, Black women have the highest maternal mortality rate (XX/100k), concentrated in counties like [X], [Y]. 
                    Key drivers include low prenatal visit rates (avg. 9.2)
                    
                    **Recommended Action:** Increase funding for prenatal care programs in rural and underserved areas, with targeted outreach to Black and Indigenous women.
                    """
            except Exception as e:
                response = f"""
                Based on available data, we can provide insights about women's health in the Deep South.
                
                **Note:** Error analyzing data: {e}
                
                **Recommended Action:** Increase funding for prenatal care programs in rural and underserved areas, with targeted outreach to Black and Indigenous women.
                """
            
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
    if not merged_data.empty:
        st.subheader("📊 Data-Driven Insights")
        
        # 基本统计洞察
        try:
            # 找到数值列
            numeric_cols = merged_data.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                st.write("**Key Statistics from Merged Data:**")
                for col in numeric_cols[:5]:  # 显示前5个
                    mean_val = merged_data[col].mean()
                    min_val = merged_data[col].min()
                    max_val = merged_data[col].max()
                    st.write(f"- {col}: Mean = {mean_val:.2f}, Range = {min_val:.2f} - {max_val:.2f}")
            
            # 添加基于数据的洞察
            st.subheader("🎯 Key Opportunities")
            if 'total_births' in merged_data.columns and 'gap_score' in merged_data.columns:
                # 先按州聚合核心指标
                state_aggregated = merged_data.groupby('state').agg({
                    'total_births': 'sum',
                    'gap_score': 'mean'
                }).reset_index()
                
                # 计算所有州的最大总出生数
                max_births = state_aggregated['total_births'].max() if not state_aggregated['total_births'].empty else 1
                
                # 用聚合后的指标重新计算州级机会指数
                state_aggregated['opportunity_index'] = (state_aggregated['total_births'] / max_births) * state_aggregated['gap_score']
                
                # 按州分析
                state_opportunity = state_aggregated.nlargest(3, 'opportunity_index')
                st.write("**Top 3 Opportunity States:**")
                for i, row in state_opportunity.iterrows():
                    st.write(f"{i+1}. {row['state']} - Opportunity Index: {row['opportunity_index']:.2f}")
        except Exception as e:
            st.warning(f"⚠️ Could not generate data insights: {e}")
    else:
        st.info("ℹ️ No merged data available. Please upload both CDC and HRSA data files to generate insights.")

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
    
    # 添加整合后的CSV文件下载
    st.subheader("📊 Merged Data Download")
    st.write("Download the complete merged dataset of CDC and HRSA data for detailed analysis. This is highly valuable for investors.")
    
    if not merged_data.empty:
        # 创建CSV下载链接
        import io
        
        def get_csv_download_link(df, filename):
            """生成CSV文件的下载链接"""
            # 创建CSV缓冲区
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_bytes = csv_buffer.getvalue().encode()
            b64 = base64.b64encode(csv_bytes).decode()
            return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Merged Data ({len(df)} rows)</a>'
        
        # 生成下载链接
        csv_link = get_csv_download_link(merged_data, "Deep_South_FemTech_Merged_Data.csv")
        st.markdown(csv_link, unsafe_allow_html=True)
        
        # 显示数据预览
        with st.expander("📋 Data Preview"):
            st.dataframe(merged_data.head())
    else:
        st.info("ℹ️ No merged data available. Please upload both CDC and HRSA data files to generate the merged dataset.")
    
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