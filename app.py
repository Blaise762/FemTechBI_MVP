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

# 侧边栏添加数据上传功能
with st.sidebar.expander("📁 Upload Data", expanded=True):
    st.markdown("Upload CSV or Excel files for custom data analysis")
    st.markdown("*Note: Currently accepting any format for testing purposes*")
    st.markdown("*For internal testing only – Production will auto-load CDC/HRSA data*")
    
    # 双文件上传
    cdc_file = st.file_uploader("Upload CDC Data File", type=["csv", "xlsx", "xls"])
    hrsa_file = st.file_uploader("Upload HRSA Data File", type=["csv", "xlsx", "xls"])

# 加载数据
cdc_data = pd.DataFrame()
hrsa_data = pd.DataFrame()
merged_data = pd.DataFrame()
mapped_cdc = pd.DataFrame()
mapped_hrsa = pd.DataFrame()

# 加载CDC数据
if cdc_file:
    cdc_file_type = 'csv' if cdc_file.name.endswith('.csv') else 'excel'
    cdc_data = load_data(cdc_file, cdc_file_type)

# 加载HRSA数据
if hrsa_file:
    hrsa_file_type = 'csv' if hrsa_file.name.endswith('.csv') else 'excel'
    hrsa_data = load_data(hrsa_file, hrsa_file_type)

# 清理并映射数据
mapped_cdc = clean_and_map_cdc_data(cdc_data)
mapped_hrsa = clean_and_map_hrsa_data(hrsa_data)

# 侧边栏添加过滤器
with st.sidebar.expander("🔍 Filters", expanded=True):
    # 深南部6州过滤器
    st.markdown("**Deep South States Filter**")
    selected_states = st.multiselect(
        "Select states to analyze",
        options=["AL", "FL", "GA", "LA", "MS", "SC"],
        default=["AL", "FL", "GA", "LA", "MS", "SC"]
    )

    # 年份筛选框
    st.markdown("\n**Year Filter**")
    # 从映射后的CDC数据中获取年份
    years = []
    if not mapped_cdc.empty and 'year' in mapped_cdc.columns:
        # 确保year列是数值类型
        mapped_cdc['year'] = pd.to_numeric(mapped_cdc['year'], errors='coerce')
        # 去重并排序
        years = sorted(mapped_cdc['year'].dropna().unique())
        # 过滤掉非数值
        years = [int(year) for year in years if isinstance(year, (int, float)) and not np.isnan(year)]
    
    if years:
        selected_years = st.multiselect(
            "Select years to analyze",
            options=years,
            default=years
        )
    else:
        selected_years = []
        st.info("ℹ️ No year data available in CDC file.")



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

# 新增：地图绘制辅助函数
def create_state_choropleth(df, metric_col='gap_score', title="Healthcare Gap Score by State"):
    """创建Deep South 6州的交互式分级着色地图
    
    参数:
    df: 合并后的数据集 (merged_data)
    metric_col: 用于着色的指标列 (gap_score/total_births/opportunity_index)
    title: 地图标题
    """
    if df.empty or metric_col not in df.columns:
        return None
    
    # 1. 聚合州级数据（确保每个州只有一条记录）
    state_map_data = df.groupby('state').agg({
        metric_col: 'mean',
        'total_births': 'sum',
        'gap_score': 'mean'
    }).reset_index()
    
    # 2. 绘制美国州级地图（使用Plotly内置数据）
    fig = px.choropleth(
        state_map_data,
        locations='state',  # 州简称
        locationmode="USA-states",  # 使用美国州模式
        color=metric_col,
        color_continuous_scale=["#B2AC88", "#FF7F50", "#FF4500"],  # 暖色调适配现有风格
        scope="usa",  # 限定地图范围为美国本土
        title=title,
        hover_data={
            'state': True,
            metric_col: ':,.2f',
            'total_births': ':,.0f',
            'gap_score': ':,.2f'
        }  # 鼠标悬浮显示的字段
    )

    # 4. 美化地图样式
    fig.update_layout(
        title_font=dict(size=18, weight="bold"),
        coloraxis_colorbar=dict(
            title=metric_col.replace('_', ' ').title(),
            tickformat=',.2f'
        ),
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0},
    )
    
    # 5. 只显示Deep South 6州（聚焦目标区域）
    fig.update_geos(
        fitbounds="locations",  # 自动适配选中的州
        visible=False
    )
    
    return fig

# 执行数据关联
merged_data = merge_data(mapped_cdc, mapped_hrsa)

# 应用深南部州过滤器
if not merged_data.empty and selected_states:
    merged_data = merged_data[merged_data['state'].isin(selected_states)]

# 应用年份过滤器
if not merged_data.empty and selected_years:
    merged_data = merged_data[merged_data['year'].isin(selected_years)]

# 暂时使用数据变量
state_data = mapped_cdc  # 暂时使用映射后的CDC数据作为州级数据


# 顶部标签页导航
# 添加自定义CSS来美化标签页
st.markdown('''
<style>
.stTabs {
    position: sticky;
    top: 0;
    z-index: 100;
    background-color: white;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab-list"] {
    display: flex;
    justify-content: space-between;
    gap: 0;
    padding: 0;
    margin: 0;
}

.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: bold;
    flex: 1;
    text-align: center;
    padding: 12px 0;
    margin: 0;
    transition: all 0.3s ease;
    border-radius: 0;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #FF7F50;
    color: white;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #FFA07A;
    color: white;
}
</style>
''', unsafe_allow_html=True)

# 管理标签页状态
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# 创建标签页
st.title("FemTech BI Dashboard")
tab_titles = ["🏠 Home", "📊 Dashboard", "🎯 Gap & Opportunity", "🤖 AI Insights", "💾 Download Center"]
tabs = st.tabs(tab_titles)

# 首页
with tabs[0]:
    st.title("FemTech BI Dashboard - Deep South")
    st.subheader("Equity-Centered Insights for Women's Health Innovation")
    st.info("📅 **Data Note:** Dataset currently runs through 2024.")
    
    # Hero区域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Our Vision
        We are building a regionally focused, equity-centered FemTech Business Intelligence platform that tracks data and insights across six Deep South states (GA, FL, AL, MS, LA, SC).
        
        ### Who We Serve
        - **Founders** (seeking opportunity zones, data-backed strategy)
        - **Funders** (impact investors, grantmakers, VCs)
        - **Systems** (health orgs, policymakers, accelerators)
        """)
        

    
    with col2:
        st.markdown("### Deep South States")
        # 替换原有静态列表 + 提示 → 嵌入交互式地图
        if not merged_data.empty:
            # 绘制Gap Score地图
            map_fig = create_state_choropleth(
                merged_data,
                metric_col='gap_score',
                title="Healthcare Gap Score (HPSA) - Deep South States"
            )
            if map_fig:
                st.plotly_chart(map_fig, width='stretch')
            else:
                st.info("📊 Map data unavailable. Please ensure merged data contains gap_score.")
        else:
            # 无数据时显示静态信息 + 提示
            st.markdown("""
            - Georgia (GA)
            - Florida (FL)
            - Alabama (AL)
            - Mississippi (MS)
            - Louisiana (LA)
            - South Carolina (SC)
            """)
            st.info("📁 Upload CDC and HRSA data files to see interactive map visualization.")
    
    # 表单捕获功能
    st.markdown("""
    ---
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
                st.rerun()
            else:
                st.error("Please fill in at least your name and email.")
    else:
        st.success("You have access to the dashboard. Click 'Explore the Dashboard' to begin.")

# 仪表板视图
with tabs[1]:
    if st.session_state.form_completed:
        if not merged_data.empty:
            st.title("Deep South FemTech Decision Center")
            st.subheader("Layout 2.0 - Equity-Centered Insights")
            st.info("📅 **Data Note:** Dataset currently runs through 2024.")
            
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
                            st.plotly_chart(fig_age, width='stretch')
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
                                st.plotly_chart(fig_trend, width='stretch')
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
with tabs[2]:
    st.title("Gap & Opportunity Analysis")
    st.info("📅 **Data Note:** Dataset currently runs through 2024.")
    
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
            
            # 添加分类标签
            def classify_state(row, median_births, median_gap):
                if row['total_births'] >= median_births and row['gap_score'] >= median_gap:
                    return "High Need + High Market"
                elif row['total_births'] < median_births and row['gap_score'] >= median_gap:
                    return "High Need + Low Resources"
                elif row['total_births'] >= median_births and row['gap_score'] < median_gap:
                    return "Emerging Opportunity"
                else:
                    return "Stable Market"
            
            median_births = state_aggregated['total_births'].median()
            median_gap = state_aggregated['gap_score'].median()
            state_aggregated['category'] = state_aggregated.apply(classify_state, axis=1, median_births=median_births, median_gap=median_gap)
            
            # 显示机会指数最高的前10个州
            top_opportunities = state_aggregated.nlargest(10, 'opportunity_index')[['state', 'category', 'total_births', 'gap_score', 'opportunity_index']]
            
            st.subheader("🎯 Top Opportunity Zones")
            
            # 显示Top 3 Priority Regions
            st.markdown("### ⭐ Top 3 Priority Regions")
            top3 = state_aggregated.nlargest(3, 'opportunity_index')
            for i, row in top3.iterrows():
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #FF7F50;">
                    <h4>#{i+1} {row['state']} - {row['category']}</h4>
                    <p><strong>Total Births:</strong> {row['total_births']:,.0f} | <strong>Gap Score:</strong> {row['gap_score']:.2f} | <strong>Opportunity Index:</strong> {row['opportunity_index']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("ℹ️ How Opportunity Index is Calculated", expanded=False):
                st.write("**Opportunity Index Formula:**")
                st.code("Opportunity Index = (State_Total_Births / Max_State_Births) × State_Average_HPSA_Score")
                st.write("**What it means:**")
                st.write("- **State_Total_Births**: Total number of births in the state (market size)")
                st.write("- **Max_State_Births**: Highest birth count among all states (for normalization)")
                st.write("- **State_Average_HPSA_Score**: Healthcare Professional Shortage Area score (need severity)")
                st.write("**Why this matters:**")
                st.write("- Combines market size (births) with need severity (HPSA score)")
                st.write("- Identifies regions with both high demand and significant healthcare gaps")
                st.write("- Perfect for founders and investors seeking high-impact opportunities")
            
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
with tabs[3]:
    st.title("AI-Powered Insights (Beta)")
    st.markdown("Ask a question about Deep South women's health data")
    st.info("💡 **Note:** This AI Insights feature is in preview. Full GPT integration coming soon!")
    
    # Q&A框
    user_query = st.text_input(
        "e.g., 'Where is Black maternal mortality highest in Alabama?'", 
        key="ai_query"
    )
    
    if user_query:
        with st.spinner("Generating insight..."):
            # 基于实际数据生成动态响应
            response = ""
            
            # 尝试从合并数据中获取真实值
            try:
                if not merged_data.empty:
                    # 构建数据摘要
                    data_summary = ""
                    
                    # 1. 基本数据概览
                    data_summary += f"Merged dataset contains {len(merged_data)} records across {merged_data['state'].nunique()} states.\n"
                    
                    # 2. 核心指标分析
                    if 'gap_score' in merged_data.columns and 'total_births' in merged_data.columns:
                        # 使用临时变量计算综合得分
                        composite_score = merged_data['gap_score'] * merged_data['total_births']
                        
                        # 按州计算平均综合得分
                        state_scores = composite_score.groupby(merged_data['state']).mean().reset_index()
                        state_scores.columns = ['state', 'composite_score']
                        # 找到综合得分最高的州
                        top_state = state_scores.nlargest(1, 'composite_score').iloc[0]
                        
                        # 获取该州的详细数据
                        state_data = merged_data[merged_data['state'] == top_state['state']].iloc[0]
                        
                        data_summary += f"Top opportunity state: {top_state['state']} with composite score of {top_state['composite_score']:.2f}.\n"
                        data_summary += f"HPSA Score: {state_data['gap_score']:.2f}, Total Births: {state_data['total_births']:,.0f}.\n"
                    
                    # 3. 种族维度分析（如果存在race列）
                    if 'race' in merged_data.columns:
                        race_counts = merged_data['race'].value_counts()
                        data_summary += f"\nRace distribution: {race_counts.to_dict()}.\n"
                        
                        # 按种族聚合分析
                        if 'total_births' in merged_data.columns:
                            race_births = merged_data.groupby('race')['total_births'].sum().reset_index()
                            data_summary += f"Births by race: {dict(zip(race_births['race'], race_births['total_births']))}.\n"
                    
                    # 4. 生成动态洞察
                    # 确保top_state变量存在
                    top_state_info = ""
                    top_state_name = ""
                    if 'top_state' in locals():
                        top_state_name = top_state['state']
                        top_state_info = f"- The state with the most significant healthcare gap is {top_state_name}, presenting a prime opportunity for FemTech innovation\n"
                    
                    response = f"""
                    ## AI-Generated Insight
                    
                    Based on the analysis of your uploaded data, here are key insights:
                    
                    **Data Summary:**
                    {data_summary}
                    
                    **What This Trend Means:**
                    {top_state_info}
                    - The data reveals significant variation in healthcare access across Deep South states, with some regions facing far greater challenges than others
                    - High HPSA scores combined with substantial birth volumes indicate clear market demand paired with unmet healthcare needs
                    
                    **Why This Matters:**
                    - Regions with both high need and large market size represent the most compelling opportunities for impact and business success
                    - Addressing these gaps can significantly improve maternal health outcomes while building sustainable FemTech businesses
                    - The Deep South region presents unique opportunities for targeted innovation that can serve as national models
                    
                    **Who Should Act & How:**
                    - **Founders**: Prioritize {top_state_name if top_state_name else 'high-opportunity states'} for launching maternal health solutions, focusing on accessibility and cultural relevance
                    - **Investors**: Allocate capital to solutions targeting these high-need, high-potential regions for maximum impact and ROI
                    - **Healthcare Systems**: Partner with local communities and tech innovators to implement scalable solutions
                    - **Policymakers**: Use this data to inform resource allocation and policy decisions
                    
                    **Key Opportunities:**
                    - Targeted interventions should focus on areas with high HPSA scores and substantial birth rates
                    {"- Race-based disparities exist, with potential for culturally competent targeted outreach programs" if 'race' in merged_data.columns else ""}
                    
                    **Immediate Next Steps:**
                    {f"1. **Founders**: Conduct on-the-ground research in {top_state_name} to understand specific community needs\n" if top_state_name else "1. **Founders**: Conduct on-the-ground research in top opportunity states to understand specific community needs\n"}
                    2. **Investors**: Map the existing FemTech ecosystem in these regions to identify gaps
                    3. **Healthcare Systems**: Pilot telehealth solutions to improve access in rural areas
                    4. **All Stakeholders**: Establish partnerships with local community organizations to ensure solutions are rooted in local needs
                    
                    *This insight was generated based on your actual data. For more detailed analysis, consider integrating with OpenAI API.*
                    """
                else:
                    response = """
                    ## Data Availability Notice
                    
                    No merged data is currently available for analysis. Please upload both CDC and HRSA data files to generate meaningful insights.
                    
                    Once data is uploaded, this system will automatically:
                    1. Analyze healthcare gaps across Deep South states
                    2. Identify top opportunity areas based on HPSA scores and birth rates
                    3. Generate race-specific insights (if race data is available)
                    4. Provide targeted investment recommendations
                    """
            except Exception as e:
                response = f"""
                ## Analysis Error
                
                An error occurred while analyzing your data: {e}
                
                Please ensure your data files contain the necessary columns (state, births, HPSA score) and try again.
                
                For optimal results, upload:
                - CDC data with birth statistics by state and year
                - HRSA data with HPSA scores by state
                - Include race data for more comprehensive insights
                """
            
            # 使用markdown显示，支持更好的格式渲染
            st.markdown(response)
    
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
            
            # 种族维度分析（如果存在race列）
            if 'race' in merged_data.columns:
                st.subheader("👥 Racial Dimensions")
                race_counts = merged_data['race'].value_counts()
                st.write("**Race Distribution:**")
                for race, count in race_counts.items():
                    st.write(f"- {race}: {count} records")
                
                # 按种族分析核心指标
                if 'total_births' in merged_data.columns:
                    race_births = merged_data.groupby('race')['total_births'].sum().reset_index()
                    st.write("**Total Births by Race:**")
                    for _, row in race_births.iterrows():
                        st.write(f"- {row['race']}: {row['total_births']:,.0f}")
            
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
with tabs[4]:
    st.title("Download Center")
    
    st.info("📅 **Data Note:** Dataset currently runs through 2024.")
    
    st.subheader("Deep South FemTech Snapshot")
    st.write("Download our comprehensive snapshot of FemTech innovation and health equity in the Deep South.")
    
    # 标记为Coming Soon
    st.warning("🚧 **Coming Soon:** Deep South FemTech Snapshot PDF download will be available in a future update.")
    
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