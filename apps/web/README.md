# 碳眸 Web 前端

`apps/web` 是碳眸校园低碳行为与水电预测平台的前端驾驶舱应用。

## 运行

```powershell
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## 构建

```powershell
npm.cmd run build
```

## 当前页面

- `src/features/dashboard/DashboardView.vue`：驾驶舱主页面。
- `src/features/dashboard/data/campusData.ts`：临时静态数据，后续替换为后端 API。
- `src/features/dashboard/components/BuildingMap.vue`：中兴大学楼栋关系示意图。
- `src/shared/components/AppChart.vue`：ECharts 通用封装。
