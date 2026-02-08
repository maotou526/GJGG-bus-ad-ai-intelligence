/*
 * @Description: 首页仪表板API接口
 * @Version: 1.0
 * @Date: 2025-01-27
 */
import { request } from '/@/utils/service';

/**
 * 首页仪表板数据响应接口
 */
export interface DashboardData {
	// 4个关键指标卡片
	total_passenger_flow: number;      // 总客流量
	operating_lines: number;           // 运营线路数
	operating_vehicles: number;        // 运营车辆数
	average_load_rate: number;         // 平均载客率
	total_passenger_flow_trend: number; // 总客流量变化趋势（百分比）
	operating_lines_trend: number;      // 运营线路变化趋势（百分比）
	operating_vehicles_trend: number;   // 运营车辆变化趋势（百分比）
	average_load_rate_trend: number;   // 平均载客率变化趋势（百分比）
	
	// TOP10线路
	top_routes: TopRoute[];
}

/**
 * TOP10线路接口
 */
export interface TopRoute {
	id: number;
	name: string;
	company: string;
	passengers: number;
}

/**
 * 客流趋势数据响应接口
 */
export interface FlowTrendData {
	// 24小时数据
	hourly_data: HourlyFlowData[];
	// 汇总数据
	total_on_board: number;  // 总上车人数
	total_off_board: number; // 总下车人数
}

/**
 * 每小时客流数据接口
 */
export interface HourlyFlowData {
	hour: string;      // 时间点，如 "06:00"
	on_board: number;  // 上车人数
	off_board: number; // 下车人数
}

/**
 * 线路状态数据响应接口
 */
export interface RoadlineStatus {
	normal: number;      // 正常运营
	suspended: number;   // 暂停运营
	adjusted: number;    // 调整运营
	special: number;     // 特殊运营（可选）
}

/**
 * 热门站点TOP10响应接口
 */
export interface HotStop {
	id: number;
	name: string;
	location: string;    // 区属
	passengers: number;  // 客流量
}

/**
 * 热门区域TOP10响应接口
 */
export interface HotDistrict {
	id: number;
	name: string;
	type: string;        // 区域类型
	flow: number;        // 日均客流
}

/**
 * 获取首页仪表板数据
 * @param date 日期，格式：YYYY-MM-DD
 * @returns 首页仪表板数据
 */
export function GetDashboardData(date: string) {
	return request({
		url: '/api/system/home/dashboard-data/',
		method: 'get',
		params: {
			date: date
		},
	});
}

/**
 * 获取客流趋势数据
 * @param date 日期，格式：YYYY-MM-DD
 * @returns 客流趋势数据
 */
export function GetFlowTrendData(date: string) {
	return request({
		url: '/api/system/home/flow-trend-data/',
		method: 'get',
		params: {
			date: date
		},
	});
}

/**
 * 获取线路状态数据
 * @param date 日期，格式：YYYY-MM-DD
 * @returns 线路状态数据
 */
export function GetRoadlineStatus(date: string) {
	return request({
		url: '/api/system/home/roadline-status/',
		method: 'get',
		params: {
			date: date
		},
	});
}

/**
 * 获取热门站点TOP10
 * @param date 日期，格式：YYYY-MM-DD
 * @returns 热门站点TOP10数据
 */
export function GetHotStops(date: string) {
	return request({
		url: '/api/system/home/hot-stops/',
		method: 'get',
		params: {
			date: date
		},
	});
}

/**
 * 获取热门区域TOP10
 * @param month 月份，格式：YYYY-MM
 * @returns 热门区域TOP10数据
 */
export function GetHotDistricts(month: string) {
	return request({
		url: '/api/system/home/hot-districts/',
		method: 'get',
		params: {
			month: month
		},
	});
}

