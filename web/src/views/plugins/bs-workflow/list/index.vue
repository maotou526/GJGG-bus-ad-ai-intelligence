<template>
  <fs-page class="workflow-scheme-page">
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <!-- 自定义操作栏右侧按钮 -->
      <template #actionbar-right>
        <el-button icon="Download" @click="handleExport" v-auth="'NWFScheme:Export'">导出</el-button>
        <el-button icon="Upload" @click="handleImport" v-auth="'NWFScheme:Import'">导入</el-button>
      </template>
    </fs-crud>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" :title="`预览流程：${previewTitle}`" width="90%"
            :close-on-click-modal="true" destroy-on-close top="5vh" class="scheme-preview-dialog">
      <div class="preview-designer-wrapper" style="height: 600px;">
        <Designer v-if="previewVisible && previewContent" :init-content="previewContent" :read-only="true" />
        <el-empty v-else-if="previewVisible && !previewLoading" description="暂无流程内容" />
        <div v-if="previewLoading" class="preview-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
      </div>
    </el-dialog>

    <!-- 表单对话框 - 使用 form.vue 组件 -->
    <el-dialog v-model="formVisible" :title="formMode === 'create' ? '新增流程模板' : '编辑流程模板'" width="90%"
            :close-on-click-modal="false" destroy-on-close top="5vh" class="scheme-form-dialog">
      <template #default>
        <div class="dialog-body-wrapper">
          <workflow-scheme-form v-if="formVisible" ref="schemeFormRef" :mode="formMode" :data-id="currentDataId"
                  :visible="formVisible" @close="handleFormClose" @refresh="handleFormRefresh" />
        </div>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <el-button :disabled="currentStep == 0" @click="handlePrev" size="large">
            <el-icon>
              <ArrowLeft />
            </el-icon>
            上一步
          </el-button>
          <el-button v-show="currentStep < 2" type="primary" @click="handleNext" size="large">
            下一步
            <el-icon>
              <ArrowRight />
            </el-icon>
          </el-button>
          <el-button type="warning" @click="handleDraftSave" size="large">
            <el-icon>
              <Document />
            </el-icon>
            保存草稿
          </el-button>
          <el-button v-show="currentStep === 2" type="success" @click="handleFinish" size="large">
            <el-icon>
              <Check />
            </el-icon>
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </fs-page>
</template>

<script lang="ts">
import { onMounted, defineComponent, ref, computed } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { ArrowLeft, ArrowRight, Check, Document, Loading } from '@element-plus/icons-vue';
import createCrudOptions from './crud';
import WorkflowSchemeForm from './form.vue';
import Designer from '../components/Designer/index.vue';
import { GetFormData } from '../api/scheme';
import { ElMessage } from 'element-plus';

export default defineComponent({
  name: 'WorkflowSchemeList',
  components: { WorkflowSchemeForm, Designer, ArrowLeft, ArrowRight, Check, Document, Loading },
  setup() {
    // 表单对话框状态
    const formVisible = ref(false);
    const formMode = ref<'create' | 'update'>('create');
    const currentDataId = ref<string | number | undefined>(undefined);
    const schemeFormRef = ref<any>(null);

    // 预览对话框状态
    const previewVisible = ref(false);
    const previewTitle = ref('');
    const previewContent = ref<any>(null);
    const previewLoading = ref(false);

    // 当前步骤（从子组件获取）
    const currentStep = computed(() => {
      // 这里的 activeStep 是通过 expose 出来的 getter 获取的，已经是解包后的值，不需要 .value
      // 由于访问的是组件实例的属性，Vue 的响应式系统会自动追踪依赖
      const step = schemeFormRef.value?.activeStep ?? 0;
      // console.log('currentStep:', step);
      return step;
    });

    // 打开新增表单
    const handleAdd = () => {
      formMode.value = 'create';
      currentDataId.value = undefined;
      formVisible.value = true; // ← 这行被误删了，现在加回来
    };

    // 打开编辑表单
    const handleEdit = (row: any) => {
      formMode.value = 'update';
      currentDataId.value = row.id;
      formVisible.value = true;
    };

    // 打开预览
    const handlePreview = async (row: any) => {
      previewTitle.value = row.name || '未命名流程';
      previewContent.value = null;
      previewLoading.value = true;
      previewVisible.value = true;

      try {
        const res = await GetFormData(row.id);
        if (res.code === 2000 && res.data?.scheme?.content) {
          previewContent.value = JSON.parse(res.data.scheme.content);
        }
      } catch (e) {
        console.error('加载流程内容失败', e);
        ElMessage.error('加载流程内容失败');
      } finally {
        previewLoading.value = false;
      }
    };

    // 传递回调函数给 crud 配置
    const { crudBinding, crudRef, crudExpose } = useFs({
      createCrudOptions: (props: any) => createCrudOptions({
        ...props,
        onAdd: handleAdd,
        onEdit: handleEdit,
        onPreview: handlePreview
      })
    });

    // 导出
    const handleExport = () => {
      const selected = crudRef.value?.getSelectedRows();
      if (!selected || selected.length === 0) {
        ElMessage.warning('请选择要导出的记录');
        return;
      }
      ElMessage.info('导出功能待实现');
    };

    // 导入
    const handleImport = () => {
      ElMessage.info('导入功能待实现');
    };

    // 关闭表单对话框
    const handleFormClose = () => {
      formVisible.value = false;
    };

    // 刷新列表
    const handleFormRefresh = () => {
      formVisible.value = false;
      ElMessage.success('保存成功');
      crudExpose.doRefresh();
    };

    // 按钮操作方法
    const handlePrev = () => {
      schemeFormRef.value?.handlePrev();
    };

    const handleNext = () => {
      schemeFormRef.value?.handleNext();
    };

    const handleDraftSave = () => {
      schemeFormRef.value?.handleDraftSave();
    };

    const handleFinish = () => {
      schemeFormRef.value?.handleFinish();
    };

    // 页面打开后获取列表数据
    onMounted(async () => {
      crudExpose.doRefresh();
    });

    return {
      crudBinding,
      crudRef,
      formVisible,
      formMode,
      currentDataId,
      schemeFormRef,
      currentStep,
      previewVisible,
      previewTitle,
      previewContent,
      previewLoading,
      handleExport,
      handleImport,
      handleFormClose,
      handleFormRefresh,
      handlePrev,
      handleNext,
      handleDraftSave,
      handleFinish,
    };
  },
});
</script>

<style scoped lang="scss">
.workflow-scheme-page {
  height: 100%;
}
</style>

<style lang="scss">
// 非 scoped 样式，专门用于这个对话框，覆盖 Element Plus 的默认样式
// 使用更高优先级的选择器来覆盖全局样式
.el-overlay .el-dialog.scheme-form-dialog {
  display: flex;
  flex-direction: column;
  margin: 0 auto; // 居中

  .el-dialog__body {
    // 使用 flex 布局让 body 自适应
    flex: 1;
    height: calc(85vh - 140px) !important; // 稍微调整高度计算，避免在小屏下溢出
    max-height: 800px;
    padding: 0 !important; // 强制去除 padding
    overflow: hidden !important;

    .dialog-body-wrapper {
      height: 100%;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }

  .el-dialog__footer {
    border-top: 1px solid #e6e6e6;
    background: #fff;
    padding: 12px 20px; // 稍微减小内边距
    z-index: 100; // 确保在最上层

    .dialog-footer {
      display: flex;
      justify-content: center; // 按钮居中
      gap: 15px;

      .el-button {
        min-width: 100px;
        padding: 10px 20px;

        &+.el-button {
          margin-left: 0; // 清除默认 margin-left，使用 gap 控制
        }
      }
    }
  }
}

// 预览对话框样式
.el-overlay .el-dialog.scheme-preview-dialog {
  .el-dialog__body {
    padding: 0 !important;
  }

  .preview-designer-wrapper {
    position: relative;
  }

  .preview-loading {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.9);
    gap: 10px;
    color: #909399;
    font-size: 14px;

    .el-icon {
      font-size: 24px;
    }
  }
}
</style>
