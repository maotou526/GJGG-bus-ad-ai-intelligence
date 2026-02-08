<template>
    <div class="workflow-scheme-form-component">
        <scheme-wizard v-if="dataLoaded" ref="wizardRef" :dialog-status="dialogStatus" :scheme-data="schemeData"
                @close="handleClose" @refresh="handleRefresh" />
        <div v-else class="loading-container">
            <el-skeleton :rows="10" animated />
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import SchemeWizard from '../components/SchemeWizard.vue';
import { GetFormData } from '../api/scheme';
import { ElMessage } from 'element-plus';

export default defineComponent({
    name: 'WorkflowSchemeFormComponent',
    components: { SchemeWizard },
    props: {
        // 对话框状态：create 或 update
        mode: {
            type: String,
            default: 'create'
        },
        // 编辑时的数据 ID（scheme_info_id）
        dataId: {
            type: [String, Number],
            default: null
        },
        // 是否显示（用于触发数据加载）
        visible: {
            type: Boolean,
            default: false
        }
    },
    emits: ['close', 'refresh'],
    setup(props, { emit, expose }) {
        const dialogStatus = ref<'create' | 'update'>('create');
        const schemeData = ref<any>(null);
        const dataLoaded = ref(false);
        const wizardRef = ref<any>(null);

        // 关闭表单
        const handleClose = () => {
            emit('close');
        };

        // 刷新后通知父组件
        const handleRefresh = () => {
            emit('refresh');
        };

        // 加载数据
        const loadData = async () => {
            dataLoaded.value = false;
            dialogStatus.value = props.mode as 'create' | 'update';

            if (props.mode === 'update' && props.dataId) {
                try {
                    // 使用新的 GetFormData API，返回 { info, scheme, authList } 格式
                    const res: any = await GetFormData(props.dataId);
                    schemeData.value = res.data || res;
                    dataLoaded.value = true;
                } catch (e) {
                    console.error(e);
                    ElMessage.error('加载数据失败');
                    emit('close');
                }
            } else {
                // 新增模式
                schemeData.value = null;
                dataLoaded.value = true;
            }
        };

        // 监听 visible 变化，当对话框打开时加载数据
        onMounted(() => {
            if (props.visible) {
                loadData();
            }
        });

        // 暴露 SchemeWizard 的属性和方法给父组件
        // 直接暴露 ref 保持响应性
        expose({
            get activeStep() {
                return wizardRef.value?.activeStep;
            },
            handlePrev: () => wizardRef.value?.handlePrev(),
            handleNext: () => wizardRef.value?.handleNext(),
            handleDraftSave: () => wizardRef.value?.handleDraftSave(),
            handleFinish: () => wizardRef.value?.handleFinish()
        });

        return {
            dialogStatus,
            schemeData,
            dataLoaded,
            wizardRef,
            handleClose,
            handleRefresh,
        };
    },
});
</script>

<style scoped lang="scss">
.workflow-scheme-form-component {
    height: 100%;
    display: flex;
    flex-direction: column;

    .loading-container {
        padding: 20px;
        text-align: center;
    }

    :deep(.el-card) {
        border: none;
        box-shadow: none;
    }

    // 调整 SchemeWizard 内部样式
    :deep(.scheme-wizard) {
        height: 100%;
        padding: 0;
        min-height: auto;

        .wizard-footer {
            margin-top: 20px;
            padding-top: 20px;
        }
    }
}
</style>
