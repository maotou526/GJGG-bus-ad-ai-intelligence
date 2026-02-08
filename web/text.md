# 修改筛选样式 
参考的模板是 networkPanorama/BusRoadlineMetrics
1. 选控制区 样式当模板 只调整样式 不改功能
2. 原生的下拉 改成 element 下拉组件
3. 页面 组件 el-card 里的head 样式 class: text-lg font-semibold text-gray-800
4. 页面的下边距使用  mb-6 class
5. 删除 echarts title 
6. 修改 echarts grid left right 为 0   top: '10%',
7. 页面文字最小为14px
8. 图表的 h-64 改成 h-80
9. 关键指标卡片区 背景渐变   p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200  green  purple orange 根据数量增加色块
10. el-card 组件增加 shadow="never"
11. 月份改成 固定时间  24年9月