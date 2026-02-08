import { request } from "/@/utils/service";

export function useUserApi() {
	return {
		getUser: (params?: object) => {
			return request({
				url: '/api/system/user/',
				method: 'get',
				params,
			});
		},
	};
}
