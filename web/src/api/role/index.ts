import { request } from "/@/utils/service";

export function useRoleApi() {
	return {
		getRole: (params?: object) => {
			return request({
				url: '/api/system/role/',
				method: 'get',
				params,
			});
		},
	};
}
