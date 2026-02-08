<!--
 * @Description: 车辆广告资源位管理
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
-->
<template>
    <fs-page>
        <el-row class="mx-2">
            <!-- 左侧：线路-车辆树形结构 -->
            <el-col xs="24" :sm="8" :md="6" :lg="4" :xl="4" class="p-1">
                <el-card :body-style="{ height: '100%', display: 'flex', flexDirection: 'column', padding: 0 }">
                    <div class="tree-header">
                        <p class="font-mono font-black text-center text-xl pb-5">
                            线路-车辆
                            <el-tooltip effect="dark" content="勾选线路节点可全选/取消全选该线路下所有车辆，勾选车辆节点可多选，根据选中的车辆过滤资源位" placement="right">
                                <el-icon>
                                    <QuestionFilled/>
                                </el-icon>
                            </el-tooltip>
                        </p>
                        <el-input v-model="filterText" placeholder="请输入线路或车辆名称"/>
                    </div>
                    <div class="tree-content">
                        <el-tree 
                            ref="treeRef" 
                            class="font-mono font-bold leading-6 text-7xl" 
                            :data="treeData" 
                            :props="treeProps"
                            :filter-node-method="filterNode" 
                            icon="ArrowRightBold" 
                            :indent="38" 
                            highlight-current 
                            show-checkbox
                            :check-strictly="false"
                            @node-click="onTreeNodeClick"
                            @check="onTreeCheck"
                            node-key="id"
                            :default-expand-all="false"
                        >
                            <template #default="{ node, data }">
                                <element-tree-line :node="node" :showLabelLine="false" :indent="32">
                                    <span v-if="data.isRoadline" class="text-center font-black font-normal">
                                        <SvgIcon name="iconfont icon-shouye" color="var(--el-color-primary)"/>&nbsp;{{ node.label }}
                                    </span>
                                    <span v-else class="text-center font-normal">
                                        <SvgIcon name="iconfont icon-shouye"/>&nbsp;{{ node.label }}
                                    </span>
                                </element-tree-line>
                            </template>
                        </el-tree>
                    </div>
                </el-card>
            </el-col>
            
            <!-- 右侧：广告资源表格 -->
            <el-col xs="24" :sm="16" :md="18" :lg="20" :xl="20" class="p-1">
                <el-card :body-style="{ height: '100%' }">
                    <fs-crud ref="crudRef" v-bind="crudBinding">
                    </fs-crud>
                </el-card>
            </el-col>
        </el-row>
    </fs-page>
</template>

<script lang="ts" setup name="VehicleAdResourceModelViewSet">
import { onMounted, ref, watch, toRaw, h, nextTick } from 'vue';
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';
import { ElTree } from 'element-plus';
import { QuestionFilled } from '@element-plus/icons-vue';
import { getElementLabelLine } from 'element-tree-line';
import { request } from '/@/utils/service';

const ElementTreeLine = getElementLabelLine(h);

interface Tree {
    id: string;
    label: string;
    isRoadline: boolean;
    vehicleId?: string;
    roadlineId?: string;
    children?: Tree[];
}

const placeholder = ref('请输入线路或车辆名称');
const filterText = ref('');
const treeRef = ref<InstanceType<typeof ElTree>>();
const selectedVehicleIds = ref<string[]>([]);

const treeProps = {
    children: 'children',
    label: 'label',
};

watch(filterText, (val) => {
    treeRef.value!.filter(val);
});

const filterNode = (value: string, data: any) => {
    if (!value) return true;
    return String(toRaw(data)?.label ?? '').indexOf(value) !== -1;
};

let treeData = ref<Tree[]>([]);

// 兼容后端两种列表返回：
// - 分页：{ code, data: [...] }
// - 其他历史/个别接口：{ code, data: { results: [...] } }
const getListData = (resp: any): any[] => {
    const data = resp?.data;
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.results)) return data.results;
    return [];
};

// 加载线路-车辆树形数据
const loadTreeData = async () => {
    try {
        // 获取所有线路
        const roadlineRes = await request({
            url: '/api/RoadlineModelViewSet/',
            method: 'get',
            params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
        });
        
        // 获取所有车辆
        const vehicleRes = await request({
            url: '/api/VehicleModelViewSet/',
            method: 'get',
            params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
        });
        
        const roadlines = getListData(roadlineRes);
        const vehicles = getListData(vehicleRes);

        // 构建树形结构：线路 -> 车辆
        const tree: Tree[] = roadlines.map((roadline: any) => {
            const roadlineId = roadline?.id;
            const roadlineVehicles = vehicles
                .filter((v: any) => String(v?.roadline ?? '') === String(roadlineId ?? ''))
                .map((v: any) => ({
                    id: `vehicle_${v.id}`,
                    label: `${v.vehicle_plate || ''}`.trim() || `车辆ID:${v.id}`,
                    isRoadline: false,
                    vehicleId: v.id,
                }));

            return {
                id: `roadline_${roadlineId}`,
                label: roadline?.line_name || '未命名线路',
                isRoadline: true,
                roadlineId: roadlineId,
                children: roadlineVehicles.length > 0 ? roadlineVehicles : undefined,
            };
        });

        treeData.value = tree;
    } catch (error) {
        console.error('加载树形数据失败:', error);
    }
};

// 获取节点下所有车辆ID（递归）
const getAllVehicleIds = (node: any): string[] => {
    const vehicleIds: string[] = [];
    if (node?.vehicleId) {
        vehicleIds.push(node.vehicleId);
    }
    if (node?.children && Array.isArray(node.children)) {
        node.children.forEach((child: any) => {
            vehicleIds.push(...getAllVehicleIds(child));
        });
    }
    return vehicleIds;
};

// 是否正在更新选中状态（避免重复触发）
const isUpdatingChecked = ref(false);

// 树形点击事件
// el-tree 的 node-click 回调签名：(data, node, tree)
const onTreeNodeClick = (data: any) => {
    // 如果点击的是线路节点，全选/取消全选该线路下的所有车辆
    if (data?.isRoadline) {
        isUpdatingChecked.value = true;
        try {
            const checkedKeys = treeRef.value!.getCheckedKeys() as string[];
            const nodeKey = data.id;
            const isChecked = checkedKeys.includes(nodeKey);
            
            // 获取该线路下所有车辆节点的key
            const vehicleKeys = getAllVehicleIds(data).map(vid => `vehicle_${vid}`);
            
            if (isChecked) {
                // 如果线路已选中，取消选中该线路及其所有车辆
                const newCheckedKeys = checkedKeys.filter(key => key !== nodeKey && !vehicleKeys.includes(key));
                treeRef.value!.setCheckedKeys(newCheckedKeys);
            } else {
                // 如果线路未选中，选中该线路及其所有车辆
                const newCheckedKeys = [...new Set([...checkedKeys, nodeKey, ...vehicleKeys])];
                treeRef.value!.setCheckedKeys(newCheckedKeys);
            }
            // 手动触发更新过滤（因为设置了isUpdatingChecked，onTreeCheck不会重复触发）
            nextTick(() => {
                updateFilterFromChecked();
                isUpdatingChecked.value = false;
            });
        } catch (error) {
            isUpdatingChecked.value = false;
            console.error('更新选中状态失败:', error);
        }
    }
};

// 树形复选框变化事件
const onTreeCheck = (data: any, checkedInfo: any) => {
    // 如果正在更新选中状态，跳过（避免重复触发）
    if (isUpdatingChecked.value) {
        return;
    }
    updateFilterFromChecked();
};

// 根据选中的节点更新过滤条件
const updateFilterFromChecked = () => {
    const checkedKeys = treeRef.value!.getCheckedKeys() as string[];
    
    // 提取所有选中的车辆ID（只处理vehicle_开头的key）
    const vehicleIds: string[] = [];
    checkedKeys.forEach((key: string) => {
        if (key.startsWith('vehicle_')) {
            const vehicleId = key.replace('vehicle_', '');
            if (vehicleId) {
                vehicleIds.push(vehicleId);
            }
        }
    });
    
    selectedVehicleIds.value = vehicleIds;
    
    // 根据选中的车辆ID更新过滤条件
    if (vehicleIds.length > 0) {
        // 如果有选中的车辆，使用vehicle_id__in过滤
        crudExpose.doSearch({ form: { vehicle_id__in: vehicleIds.join(',') } });
    } else {
        // 如果没有选中的车辆，清空过滤
        crudExpose.doSearch({ form: {} });
    }
};

// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding });
// 你的crud配置（将左侧树选中的车辆透传给 crud，用于新增时自动填充 vehicle_id）
const { crudOptions } = createCrudOptions({ crudExpose, context: { selectedVehicleIds } });
// 初始化crud配置
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions });

// 页面打开后获取数据
onMounted(() => {
    loadTreeData();
    crudExpose.doRefresh();
});
</script>

<style lang="scss" scoped>
.el-row {
    height: 100%;

    .el-col {
        height: 100%;
    }
}

.el-card {
    height: 100%;
    overflow: hidden;
}

.tree-header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: white;
    padding: 20px;
    border-bottom: 1px solid #ebeef5;
    flex-shrink: 0;
}

.tree-content {
    flex: 1;
    overflow-y: auto;
    padding: 0 20px 20px 20px;
}

.font-normal {
    font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, SimSun, sans-serif;
}
</style>

