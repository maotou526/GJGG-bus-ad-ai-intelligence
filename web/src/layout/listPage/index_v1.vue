<!--
 * @Description: 
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-20 15:06:46
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-21 17:18:11
-->
<template>
  <div class="custom-layout">
    <div class="layout-header">
      <!-- ↓↓↓↓↓  关键插槽：查询  ↓↓↓↓ -->
      <el-card shadow="never" :body-style="{ padding: '16px' }" style="width:100%">
        <slot name="search"></slot>
        <!-- ↓↓↓↓↓  关键插槽：动作条  ↓↓↓↓ -->
        <slot name="actionbar"></slot>
      </el-card>
    </div>
    <!-- <div class="layout-top">
    </div> -->

    <!-- ✨✨✨ 新增：统计块区域 ✨✨✨ -->
    <div class="mt-[10px] layout-statistics" v-if="$slots['header-bottom']">
      <!-- ↓↓↓↓↓  关键插槽：统计块  ↓↓↓↓ -->
      <slot name="header-bottom"></slot>
    </div>

    <!-- 高度需要自适应撑开，可以通过flex:1 -->
    <div class="layout-body">
      <!-- 默认插槽 -->
      <slot></slot>
      <!-- ↓↓↓↓↓  关键插槽：表格  ↓↓↓↓ -->
      <slot name="table"></slot>

      <!-- ↓↓↓↓↓  关键插槽：表单  ↓↓↓↓ -->
      <slot name="form"></slot>
    </div>
    <div class="layout-footer">
      <!-- ↓↓↓↓↓  关键插槽：分页条  ↓↓↓↓ -->
      <slot name="pagination"></slot>
    </div>
  </div>
</template>
  
  <script lang="ts">
  import { defineComponent } from "vue";
  import { ElCard } from 'element-plus';
  /**
   * 自定义布局
   */
  export default defineComponent({
    name: "CustomLayout",
    components: {
      ElCard
    }
  });
  </script>
  
  <style lang="less">
  .custom-layout {
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 12px;
  
    .layout-header {
      width: 100%;
      padding: 0 0 10px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .layout-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 0;
    }
    .layout-statistics {
      padding: 0 0 10px 0;
    }
    .layout-body {
      flex: 1; //重要，自适应撑开高度，表格固定表头必须
      overflow-y: auto;
      padding: 0 0 10px 0;
    }
    .layout-footer {
      padding: 0;
      box-sizing: content-box;
    }
    .fs-crud-actionbar {
      display: flex;
      align-items: center;
    }
    .fs-crud-footer {
      padding: 0;
    }
    .fs-crud-pagination {
      .fs-pagination {
        .el-pagination {
          justify-content: start;
        }
      }
    }
  
    .fs-tabs-filter {
      margin-left: 10px;
    }
  }
  </style>