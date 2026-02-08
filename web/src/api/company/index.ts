import { request } from "/@/utils/service";

/**
 * 获取所有公司列表
 */
export function getAllCompanies(params?: any) {
	return request({
		url: "/api/CompanyModelViewSet/",
		method: 'get',
		params: {
			limit: 999,
			...params
		}
	});
}
