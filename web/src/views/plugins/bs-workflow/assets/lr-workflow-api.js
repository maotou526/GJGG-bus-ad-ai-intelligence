(function ($, learun) {
    "use strict";
    var tabIframeId = request('tabIframeId');  // 当前窗口ID
    var MouldeCode = request('MouldeCode');
    var type = '';    
    var wfFormParam;        // 流程表单传递参数
    var userId;             // 流程发起人
    var processId;          // 流程实例主键
    var taskId;             // 任务主键
    var scheme;             // 流程模板
    var schemeCode;         // 流程模板编号
    var currentNode;        // 当前节点

    var isFinished;         // 流程是否结束
    var pProcessId;         // 父级流程实例主键
    var pTaskId;            // 父流程任务（子流程发起节点）
    var currentIds;         // 当前需要审核的节点
    var ainfo = [];         // 审核者信息,用于打印;

    var chlidCurrentNode;   // 子流程当前节点

    window.nwflow = {
        init: {
            look: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'look';
                processId = _processId;
                taskId = _taskId;
                nwflow.getProcessInfo(processId, taskId, function (data) {
                    nwflow.loadForm(currentNode.wfForms, true);
                });
            },
            create: function (code, _processId, _taskId, _wfFormParam, _userId) {// 创建流程
                type = 'create';
                userId = _userId;
                wfFormParam = _wfFormParam;
                processId = _processId || learun.newGuid();
                schemeCode = code;

                nwflow.getSchemeByCode(code, function (data) {
                    if (data) {
                        scheme = JSON.parse(data.F_Content);
                        nwflow.scheme = scheme;
                        // 获取开始节点
                        $.each(scheme.nodes, function (_index, _item) {
                            if (_item.type == 'startround') {
                                currentNode = _item;
                                return false;
                            }
                        });
                        nwflow.loadForm(currentNode.wfForms);


                        nwflow.loadFlowInfo(scheme, [], {});
                        nwflow.loadTimeLine([], {});

                        $('#release').on('click', function () {
                            nwflow.createFlow();
                        });
                        $('#release').showBtn();
                        $('#savedraft').on('click', function () {
                            nwflow.saveDraft();
                        });
                        $('#savedraft').showBtn();
                        $('#flow-level').show();
                        if (currentNode.isTitle == '1') {
                            $('#flow-title').show();
                        }
                    }
                    
                })
            },
            draftCreate: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'draftCreate';
                userId = _userId;
                wfFormParam = _wfFormParam;
                processId = _processId;
                nwflow.getSchemeByProcessId(processId, function (data) {
                    // 获取开始节点
                    $.each(scheme.nodes, function (_index, _item) {
                        if (_item.type == 'startround') {
                            currentNode = _item;
                            return false;
                        }
                    });
                    nwflow.loadForm(currentNode.wfForms);

                    $('#release').on('click', function () {
                        nwflow.createFlow();
                    });
                    $('#release').showBtn();
                    $('#savedraft').on('click', function () {
                        nwflow.saveDraft();
                    });
                    $('#savedraft').showBtn();
                    $('#flow-level').show();
                    if (currentNode.isTitle == '1') {
                        $('#flow-title').show();
                    }

                })

            },
            againCreate: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'againCreate';
                processId = _processId;
                nwflow.getProcessInfo(processId, '', function (data) {
                    nwflow.loadForm(currentNode.wfForms);
                    $('#release').showBtn();
                    $('#release').text('重新发起');
                    $('#release').on('click', function () {
                        nwflow.againCreateFlow();
                    });
                });
            },
            audit: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'audit';
                processId = _processId;
                taskId = _taskId;
                nwflow.getProcessInfo(processId, taskId, function (data) {
                    nwflow.loadForm(currentNode.wfForms);
                    // 加载审批按钮
                    var $signBtn = $('#sign');
                    $.each(currentNode.btnList, function (_index, _item) {
                        if (_item.isHide != '1') {
                            var _class = ' btn-warning';
                            if (_item.code == 'agree') {
                                _class = ' btn-success';
                            }
                            else if (_item.code == 'disagree') {
                                _class = ' btn-danger';
                            }

                            var $btn = $('<a class="verifybtn btn ' + _class + '"  >' + _item.name + '</a>');
                            $btn[0].lrbtn = _item;
                            $signBtn.after($btn);
                        }
                    });
                    $('.verifybtn').showBtn();
                    $('.verifybtn').on('click', function () {
                        var btnData = $(this)[0].lrbtn; 
                        nwflow.auditFlow(btnData);
                    });
                    if (currentNode.isSign == "1") {
                        $('#sign').showBtn();
                        $('#sign').on('click', function () {
                            nwflow.signFlow();
                        });
                    }

                    $('#flow-des').show();
                });
            },
            signAudit: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'signAudit';
                processId = _processId;
                taskId = _taskId;
                nwflow.getProcessInfo(processId, taskId, function (data) {
                    nwflow.loadForm(currentNode.wfForms);
                    // 加载审批按钮
                    var $signBtn = $('#sign');
                    var $btn1 = $('<a class="verifybtn btn btn-success"  >同意</a>');
                    $btn1[0].lrbtn = { code: 'agree', name: '同意' };
                    $signBtn.after($btn1);
                    var $btn2 = $('<a class="verifybtn btn btn-danger"  >不同意</a>');
                    $btn2[0].lrbtn = { code: 'disagree', name: '不同意' };
                    $signBtn.after($btn2);
                    $('.verifybtn').showBtn();
                    $('.verifybtn').on('click', function () {
                        var btnData = $(this)[0].lrbtn;
                        nwflow.signAudit(btnData);
                    });

                    $signBtn.showBtn();
                    $signBtn.on('click', function () {
                        nwflow.signFlow();
                    });

                    $('#flow-des').show();
                });
            },
            refer: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'refer';
                processId = _processId;
                taskId = _taskId;
                nwflow.getProcessInfo(processId, taskId, function (data) {
                    nwflow.loadForm(currentNode.wfForms);
                    $('#confirm').showBtn().on('click', function () {
                        learun.layerConfirm('是否确认阅读！', function (res, index) {
                            if (res) {
                                // 更新任务状态
                                learun.loading(true, '确认阅读...');
                                var postData = {
                                    processId: processId,
                                    taskId: taskId
                                };
                                learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/ReferFlow', postData, function (res) {
                                    learun.loading(false);
                                    if (res.code == 200) {
                                        learun.alert.success(res.info);
                                        learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                                        tabIframeId && learun.frameTab.close(tabIframeId);
                                    }
                                });
                                top.layer.close(index);
                            }
                        });
                    });
                });
            },
            chlid: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'chlid';
                pTaskId = _taskId;
                pProcessId = _processId;

                nwflow.pTaskId = _taskId;
                nwflow.pProcessId = _processId;

                nwflow.getProcessInfo(_processId, _taskId, function (data) {
                    processId = data.info.childProcessId;
                    // 获取流程的模板
                    nwflow.getSchemeByCode(currentNode.childFlow, function (cdata) {
                        if (cdata) {
                            scheme = JSON.parse(cdata.F_Content);
                            nwflow.scheme = scheme;
                            // 获取开始节点
                            $.each(scheme.nodes, function (_index, _item) {
                                if (_item.type == 'startround') {
                                    chlidCurrentNode = _item;
                                    return false;
                                }
                            });
                            nwflow.loadForm(chlidCurrentNode.wfForms);

                            nwflow.loadFlowInfo(scheme, [], {});
                            nwflow.loadTimeLine([], {});


                            $('#release').showBtn();
                            $('#release').on('click', function () {
                                // 验证表单数据完整性
                                if (!formApi.validForm('createChlid',chlidCurrentNode.wfForms))// create创建流程
                                {
                                    return false;
                                }

                                // 保存表单数据
                                formApi.save(processId, chlidCurrentNode.wfForms, function () {
                                    // 创建流程
                                    learun.loading(true, '创建子流程...');
                                    var postData = {
                                        schemeCode: currentNode.childFlow,
                                        processId: processId,
                                        parentProcessId: pProcessId,
                                        parentTaskId: pTaskId
                                    };
                                    learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/CreateChildFlow', postData, function (res) {
                                        learun.loading(false);
                                        if (res.code == 200) {
                                            learun.alert.success(res.info);
                                            learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                                            tabIframeId && learun.frameTab.close(tabIframeId);
                                        }
                                    });
                                });
                            });
                            $('#savedraft').showBtn();
                            $('#savedraft').on('click', function () {
                                // 保存表单数据
                                formApi.save(processId, chlidCurrentNode.wfForms, function () {
                                });
                            });
                        }
                    });
                },true);
            },
            childlook: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'childlook';
                pTaskId = _taskId;
                pProcessId = _processId;
                nwflow.pTaskId = _taskId;
                nwflow.pProcessId = _processId;

                nwflow.getProcessInfo(_processId, _taskId, function (data) {
                    processId = data.info.childProcessId;
                    // 获取流程的模板
                    nwflow.getSchemeByCode(currentNode.childFlow, function (cdata) {
                        if (cdata) {
                            scheme = JSON.parse(cdata.F_Content);
                            nwflow.scheme = scheme;
                            // 获取开始节点
                            $.each(scheme.nodes, function (_index, _item) {
                                if (_item.type == 'startround') {
                                    chlidCurrentNode = _item;
                                    return false;
                                }
                            });
                            nwflow.loadForm(chlidCurrentNode.wfForms);
                            console.log(data);
                            nwflow.loadFlowInfo(scheme, data.task || [], data.info || {});
                            nwflow.loadTimeLine(data.task || [], data.info || {});
                        }
                    });
                }, true);

            },
            againChild: function (code, _processId, _taskId, _wfFormParam, _userId) {
                type = 'againChild';
                pTaskId = _taskId;
                pProcessId = _processId;

                nwflow.pTaskId = _taskId;
                nwflow.pProcessId = _processId;

                nwflow.getProcessInfo(_processId, _taskId, function (data) {
                    processId = data.info.childProcessId;
                    // 获取流程的模板
                    nwflow.getSchemeByCode(currentNode.childFlow, function (cdata) {
                        if (cdata) {
                            scheme = JSON.parse(cdata.F_Content);
                            nwflow.scheme = scheme;
                            // 获取开始节点
                            $.each(scheme.nodes, function (_index, _item) {
                                if (_item.type == 'startround') {
                                    chlidCurrentNode = _item;
                                    return false;
                                }
                            });
                            nwflow.loadForm(chlidCurrentNode.wfForms);

                            nwflow.loadFlowInfo(scheme, data.task || [], data.info || {});
                            nwflow.loadTimeLine(data.task || [], data.info || {});


                            $('#release').showBtn();
                            $('#release').on('click', function () {
                                // 验证表单数据完整性
                                if (!formApi.validForm('createChlid', chlidCurrentNode.wfForms))// create创建流程
                                {
                                    return false;
                                }

                                // 保存表单数据
                                formApi.save(processId, chlidCurrentNode.wfForms, function () {
                                    // 创建流程
                                    learun.loading(true, '创建子流程...');
                                    var postData = {
                                        schemeCode: currentNode.childFlow,
                                        processId: processId,
                                        parentProcessId: pProcessId,
                                        parentTaskId: pTaskId
                                    };
                                    learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/CreateChildFlow', postData, function (res) {
                                        learun.loading(false);
                                        if (res.code == 200) {
                                            learun.alert.success(res.info);
                                            learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                                            tabIframeId && learun.frameTab.close(tabIframeId);
                                        }
                                    });
                                });
                            });
                            $('#savedraft').showBtn();
                            $('#savedraft').on('click', function () {
                                // 保存表单数据
                                formApi.save(processId, chlidCurrentNode.wfForms, function () {
                                });
                            });
                        }
                    });
                }, true);
            }
        },

        loadForm: function (wfForms, isLook) {
            if (wfForms.length == 0) {
                $('.flow-btn').show();
            }
            else {
                var form = wfForms[0];
                console.log(form);
                var $iframes = $('#form_list_iframes');
                if (form.type == '1') {// 自定义表单
                    $iframes.append('<div id="wfFormContainer" class="form-list-container" ></div>');
                    formApi.init(form, $iframes.find('#wfFormContainer'), isLook);
                }
                else {// 系统表单
                    $iframes.append('<iframe id="wfFormIframe" class="form-list-iframe" frameborder="0" ></iframe>');
                    formApi.systemFormLoad("wfFormIframe", form.url + "?MouldeCode=" + MouldeCode, function (iframeObj) {
                        // 设置字段权限
                        iframeObj.setAuthorize && iframeObj.setAuthorize(form.authorize, isLook);
                        iframeObj.page && iframeObj.page.setAuthorize && iframeObj.page.setAuthorize(form.authorize, isLook);
                        if (userId) {// 处理流程代办发起，当前人员信息字段
                            var loginInfo = learun.clientdata.get(['userinfo']);
                            if (loginInfo.userId != userId) {
                                learun.clientdata.getAsync('user', {
                                    key: userId,
                                    callback: function (_data) {
                                        iframeObj.$('.currentInfo').each(function () {
                                            var $this = $(this);
                                            if ($this.hasClass('lr-currentInfo-company')) {
                                                $this[0].lrvalue = _data.companyId;
                                                learun.clientdata.getAsync('company', {
                                                    key: _data.companyId,
                                                    callback: function (_data) {
                                                        $this.val(_data.name);
                                                    }
                                                });
                                            }
                                            else if ($this.hasClass('lr-currentInfo-department')) {
                                                $this[0].lrvalue = _data.departmentId;
                                                learun.clientdata.getAsync('department', {
                                                    key: _data.departmentId,
                                                    callback: function (_data) {
                                                        $this.val(_data.name);
                                                    }
                                                });
                                            }
                                            else if ($this.hasClass('lr-currentInfo-user')) {
                                                $this[0].lrvalue = userId;
                                                $this.val(_data.name);
                                            }
                                        })
                                    }
                                })
                            }
                        }
                        if (iframeObj.setFormData) {
                            iframeObj.setFormData(processId, wfFormParam, userId, function () {
                                $('.flow-btn').show();
                            });
                        }
                        else if (iframeObj.page.setFormData) {
                            iframeObj.page.setFormData(processId, wfFormParam, userId, function () {
                                $('.flow-btn').show();
                            });
                        }
                        else {
                            $('.flow-btn').show();
                        }

                    });
                }
            }
        },
        loadFlowInfo: function (scheme, taskInfo, info) {
            var nodeInfoes = {};
            var strcurrentIds = String(currentIds || []);
            var history = info.TaskLogList || [];
            nwflow.nodeMap = {};
            // 当前节点处理人信息
            $.each(taskInfo, function (_index, _item) {
                var nameList = [];
                $.each(_item.nWFUserInfoList, function (_jindex, _jitem) {
                    if (_jitem.Mark == 0) {
                        nameList.push(_jitem.Id);
                    }
                });
                var point = {
                    namelist: nameList
                }
                nodeInfoes[_item.F_NodeId] = nodeInfoes[_item.F_NodeId] || [];
                nodeInfoes[_item.F_NodeId].push(point);
            });
            // 初始化工作流节点历史处理信息
            $.each(history, function (id, item) {
                nodeInfoes[item.F_NodeId] = nodeInfoes[item.F_NodeId] || [];
                nodeInfoes[item.F_NodeId].push(item);
            });
            $.each(scheme.nodes, function (_index, _item) {//0正在处理 1 已处理同意 2 已处理不同意 3 未处理 
                _item.state = '3';
                if (nodeInfoes[_item.id]) {
                    _item.history = nodeInfoes[_item.id];
                    _item.state = '1';
                }
                if (strcurrentIds.indexOf(_item.id) > -1) {
                    _item.state = '0';
                }
                if (_item.isAllAuditor == "2") {
                    _item.name += '<br/>【多人审核:';

                    if (_item.auditorType == "1") {
                        _item.name += '并行】';
                    }
                    else {
                        _item.name += '串行】';
                    }
                }
                nwflow.nodeMap[_item.id] = _item;
            });
            $('#flow').lrworkflowSet('set', { data: scheme });
        },
        loadTimeLine: function (taskInfo,info) {
            var nodelist = [];
            var history = info.TaskLogList || [];
            // 当前节点处理人信息
            $.each(taskInfo, function (_index, _item) {
                var nameList = [];
                $.each(_item.nWFUserInfoList, function (_jindex, _jitem) {
                    if (_jitem.Mark == 0) {
                        nameList.push(_jitem.Id);
                    }
                });

                var point = {
                    title: _item.F_NodeName + "【正在处理节点】",
                    people: String(nameList),
                    content: '需要其审核',
                    time: "当前"
                };
                nodelist.push(point);

            });

            // 历史审核记录
            var anodeinfo = {};
            var $anodeinfo = $('.tab-flow-audit');
            for (var i = 0, l = history.length; i < l; i++) {
                var item = history[i];

                var content = item.F_OperationName;
                if (item.F_Des) {
                    content += '<br/>【审批意见】：' + item.F_Des;
                }

                var nodeName = '';
                if (item.F_NodeId && nwflow.nodeMap[item.F_NodeId]) {
                    nodeName = nwflow.nodeMap[item.F_NodeId].name;
                }

                var point = {
                    title: item.F_NodeName || nodeName,
                    people: item.F_CreateUserId,
                    peopleName: item.F_CreateUserName,
                    content: content,
                    time: item.F_CreateDate
                };

                if (item.F_OperationCode == 'createChild' || item.F_OperationCode == 'againCreateChild') {
                    point.content = content + '<span class="lr-event" >查看</span>';
                    point.nodeId = item.F_NodeId;
                    point.processId = item.F_ProcessId;
                    point.callback = function (data) {
                        learun.layerForm({
                            id: 'LookFlowForm',
                            title: '子流程查看',
                            url: top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/LookFlowForm?nodeId=' + data.nodeId + '&processId=' + data.processId + '&type=lookChlid',
                            width: 1000,
                            height: 900,
                            maxmin: true,
                            btn: null
                        });
                    }
                }


                /*审核人信息显示*/

                if (!anodeinfo[item.F_NodeId + item.F_CreateUserId] && item.F_TaskType != '0' && item.F_TaskType != '4' && item.F_TaskType != '5' && item.F_TaskType != '6') {
                    var apoint = {};
                    apoint.type = 'anodeinfo';
                    apoint.title = point.title;

                    anodeinfo[item.F_NodeId + item.F_CreateUserId] = true;
                    var html = '<div class="auditinfo">\
                                        <div class="auditinfo-h" >'+ point.title + '</div >\
                                            <div class="auditinfo-b">';
                    if (item.F_StampImg != '' && item.F_StampImg != null && item.F_StampImg != 'null') {
                        apoint.stampImg = new Image();
                        apoint.stampImg.src = top.$.rootUrl + '/LR_NewWorkFlow/StampInfo/GetImg?keyValue=' + item.F_StampImg;

                        html += '<div class="auditinfo-s" ><img src=' + top.$.rootUrl + '/LR_NewWorkFlow/StampInfo/GetImg?keyValue=' + item.F_StampImg + '></div>';
                    }
                    if (item.F_SignImg != '' && item.F_SignImg != null && item.F_SignImg != 'null') {
                        apoint.signImg = new Image();
                        apoint.signImg.src = top.$.rootUrl + '/LR_SystemModule/Img/Down?id=' + item.F_SignImg;
                        html += '<div class="auditinfo-sg" ><img src=' + top.$.rootUrl + '/LR_SystemModule/Img/Down?id=' + item.F_SignImg + '></div>';
                    }

                    html += '<p>' + point.content + '</p>\
                                                <div class="auditinfo-n"><span>签&nbsp;&nbsp;&nbsp;&nbsp;字:&nbsp;&nbsp;</span><span uId="'+ point.people +'" >'+ point.people + '</ span></div>\
                                                <div class="auditinfo-d"><span>日&nbsp;&nbsp;&nbsp;&nbsp;期:&nbsp;&nbsp;</span><span>'+ point.time + '</span></div>\
                                            </div>\
                                    </div >';
                    apoint.content = point.content;
                    apoint.date = point.time;
                    apoint.user = point.people;

                    ainfo.push(apoint);

                    $anodeinfo.prepend(html);

                    top.learun.clientdata.getAsync('user', {
                        key: point.people,
                        callback: function (user) {
                            if (user.F_DepartmentId) {
                                top.learun.clientdata.getAsync('department', {
                                    key: user.F_DepartmentId,
                                    callback: function (department) {
                                        $('[uId="' + point.people+'"]').text('【' + department.F_FullName + '】' + user.F_RealName);
                                    }
                                });
                            }
                            else {
                                $('[uId="' + point.people + '"]').text(user.F_RealName);
                            }
                        }
                    });
                }

                nodelist.push(point);
            } 
            $('#auditinfo').lrtimeline(nodelist, isFinished);
        },

        // 流程创建
        saveDraft: function () {// 保存草稿数据
            formApi.save(processId, currentNode.wfForms, function () {
                learun.loading(true, '保存流程草稿...');
                var postData = {
                    schemeCode: shcemeCode,
                    processId: processId,
                    createUserId: userId
                };
                learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/SaveDraft', postData, function (res) {
                    learun.loading(false);
                    if (res.code == 200) {
                        learun.alert.success(res.info);
                        learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                    }
                });
            });
        },
        createFlow: function () {
            // 验证表单数据完整性
            if (!formApi.validForm(type, currentNode.wfForms))// create创建流程
            {
                return false;
            }
            var flow_level = $('#flow-level').lrGetFormData().F_Level;

            nwflow.loadNextUsers({ code: 'agree' },function (auditers) {
                // 保存表单数据
                formApi.save(processId, currentNode.wfForms, function () {
                    // 创建流程
                    learun.loading(true, '创建流程...');
                    var postData = {
                        schemeCode: shcemeCode,
                        processId: processId,
                        title: $('#F_Title').val(),
                        level: flow_level,
                        auditors: auditers,
                        createUserId: userId
                    };
                    learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/CreateFlow', postData, function (res) {
                        learun.loading(false);
                        if (res.code == 200) {
                            learun.alert.success(res.info);
                            learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                            tabIframeId && learun.frameTab.close(tabIframeId);
                        }
                    });
                });
            });
        },
        againCreateFlow: function () {
            // 验证表单数据完整性
            if (!formApi.validForm('againCreate', currentNode.wfForms))// againCreate重新创建创建流程
            {
                return false;
            }
            learun.layerConfirm('是否重新发起流程！', function (res, index) {
                if (res) {
                    formApi.save(processId, currentNode.wfForms, function () {
                        // 创建流程
                        learun.loading(true, '重新发起流程...');
                        var postData = {
                            processId: processId
                        };
                        learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/AgainCreateFlow', postData, function (res) {
                            learun.loading(false);
                            if (res.code == 200) {
                                learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                                tabIframeId && learun.frameTab.close(tabIframeId);
                            }
                        });
                    });
                    top.layer.close(index);
                }
            });
        },
        auditFlow: function (btnData) {
            // 验证表单数据完整性
            if (!formApi.validForm(btnData.code, currentNode.wfForms)) {
                return false;
            }
            top.flowAuditfn = function (signUrl, stamp) {
                console.log(signUrl, stamp);
                nwflow.loadNextUsers(btnData, function (auditers) {
                    // 保存表单数据
                    //formApi.save(processId, currentNode.wfForms, function () {
                        // 审批流程
                        learun.loading(true, '审批流程...');
                        var postData = {
                            operationCode: btnData.code,
                            operationName: btnData.name,
                            processId: processId,
                            taskId: taskId,
                            des: $('#des').val(),
                            auditors: auditers,
                            signUrl: signUrl,
                            stamp: stamp
                        };
                        learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/AuditFlow', postData, function (res) {
                            learun.loading(false);
                            if (res.code == 200) { 
                                formApi.save(processId, currentNode.wfForms, function () {  
                                    learun.alert.success(res.info);
                                    learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                                    tabIframeId && learun.frameTab.close(tabIframeId);
                                });   
                            } else {
                                learun.alert.error(res.info);
                            }
                        });
                   // });
                });
            }

            if (btnData.isSign == '1') {
                learun.layerForm({
                    id: 'SignForm',
                    title: '签名或盖章(请按着鼠标左键签字)',
                    url: top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/SignForm',
                    width: 600,
                    height: 265,
                    btn: null
                });
            }
            else {
                top.flowAuditfn("", "");
            }
        },
        signFlow: function () {
            // 验证表单数据完整性
            if (!formApi.validForm("sign", currentNode.wfForms)) {
                return false;
            }

            // 创建审批
            learun.layerForm({
                id: 'SignFlowForm',
                title: "加签",
                url: top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/SignFlowForm',
                width: 500,
                height: 400,
                callBack: function (id) {
                    return top[id].acceptClick(function (formdata) {
                        // 保存表单数据
                        formApi.save(processId, currentNode.wfForms, function () {
                            // 审批流程
                            learun.loading(true, '流程加签...');
                            var postData = {
                                des: $('#des').val(),
                                userId: formdata.auditorId,
                                processId: processId,
                                taskId: taskId
                            };
                            learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/SignFlow', postData, function (res) {
                                learun.loading(false);
                                if (res.code == 200) {
                                    learun.alert.success(res.info);
                                    learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                                    tabIframeId && learun.frameTab.close(tabIframeId);
                                }
                            });
                        });
                    });
                }
            });
        },
        signAudit: function (btnData) {
            // 验证表单数据完整性
            if (!formApi.validForm(btnData.code, currentNode.wfForms)) {
                return false;
            }
            formApi.save(processId, currentNode.wfForms, function () {
                // 审批流程
                learun.loading(true, '加签审批流程...');
                var postData = {
                    operationCode: btnData.code,
                    processId: processId,
                    taskId: taskId,
                    des: $('#des').val()
                };
                learun.httpAsyncPost(top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/SignAuditFlow', postData, function (res) {
                    learun.loading(false);
                    if (res.code == 200) {
                        learun.alert.success(res.info);
                        learun.frameTab.parentIframe().refreshGirdData && learun.frameTab.parentIframe().refreshGirdData();
                        tabIframeId && learun.frameTab.close(tabIframeId);
                    }
                });
            });
        },


        // 加载下一节点审核人
        loadNextUsers:function (btn, callback) {
            var isNext = currentNode.isNext;
            if (btn.next == '2') {
                isNext = '1';
            }

            if (isNext == '1') {// 获取下一节点数据
                var param = {
                    code: shcemeCode,
                    processId: processId,
                    taskId: taskId,
                    nodeId: currentNode.id,
                    operationCode: btn.code
                };
                learun.httpAsync('GET', top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/GetNextAuditors', param, function (data) {
                    var _flag = false;
                    $.each(data, function (_id, _list) {
                        if (_list.length > 1) {
                            _flag = true;
                            return false;
                        }
                    });
                    if (_flag) {
                        nwflow.nextUsers = data;
                        learun.layerForm({
                            id: 'SelectUserForm',
                            title: '选择下一节点审核人员',
                            url: top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/SelectUserForm',
                            width: 400,
                            height: 340,
                            callBack: function (id) {
                                return top[id].acceptClick(function (auditers) {
                                    callback && callback(JSON.stringify(auditers));

                                });
                            }
                        });
                    } else {
                        callback && callback();
                    }
                });
            }
            else {
                callback && callback();
            }
        },

        // 获取数据
        getSchemeByCode: function (code, callback) {// 根据流程模板获取表单
            learun.httpAsync('GET', top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/GetSchemeByCode', { code: code }, function (data) {
                callback && callback(data);
            });
        },
        getSchemeByProcessId: function (processId, callback) {
            learun.httpAsync('GET', top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/GetSchemeByProcessId', { processId: processId }, function (data) {
                if (data) {
                    scheme = JSON.parse(data.F_Content);
                    nwflow.scheme = scheme;
                    currentIds = data.info.currentIds || [];
                    nwflow.loadFlowInfo(scheme, data.task || [], data.info || {});
                    nwflow.loadTimeLine(data.task || [], data.info || {});
                    callback(data);
                }
            });
        },
        getProcessInfo: function (processId, taskId, callback,isChild) {
            learun.httpAsync('GET', top.$.rootUrl + '/LR_NewWorkFlow/NWFProcess/GetProcessDetails', { processId: processId, taskId: taskId }, function (data) {
                isFinished = data.info.isFinished;
                if (data) {
                    scheme = JSON.parse(data.info.Scheme);
                    nwflow.scheme = scheme;
                    // 获取当前节点
                    $.each(scheme.nodes, function (_index, _item) {
                        if (_item.id == data.info.CurrentNodeId) {
                            currentNode = _item;
                            return false;
                        }
                    });
                    currentIds = data.info.CurrentNodeIds;
                    if (data.info.parentProcessId) {
                        pProcessId = data.info.parentProcessId;
                        nwflow.pProcessId = data.info.parentProcessId;
                        $('#eye').showBtn();
                    }
                    if (!isChild) {
                        nwflow.loadFlowInfo(scheme, data.task || [], data.info || {});
                        nwflow.loadTimeLine(data.task || [], data.info || {});
                    }
                    else {
                        
                        $('#eye').showBtn();
                    }
                    callback(data);
                    console.log(data);
                }
                
            });
        }
    }

    var formIframe;
    var formApi = {
        init: function (formInfo, $container, isLook) {
            formApi.loadScheme(formInfo.formId, function (data) {
                var formScheme = JSON.parse(data.schemeEntity.F_Scheme);
                formInfo.formScheme = formScheme;
                // 编辑表格权限
                var girdMap = {};
                $.each(formInfo.authorize || [], function (_field, _item) {
                    var _ids = _field.split('|');
                    //if (isLook) {
                    //    _item.isEdit = 0;
                    //}
                    if (_ids.length > 1) {
                        if (_item.isLook != 1 || _item.isEdit != 1) {
                            girdMap[_ids[0]] = girdMap[_ids[0]] || {};
                            girdMap[_ids[0]][_ids[1]] = _item;
                        }
                    }
                });
                $.each(formScheme.data, function (_i, _item) {
                    $.each(_item.componts, function (_j, _jitem) {
                        if (_jitem.type == 'currentInfo') {
                            _jitem._userId = createUserId;
                        }
                        if ((_jitem.type == 'girdtable' || _jitem.type == 'gridtable') && girdMap[_jitem.id]) {
                            var _gird = girdMap[_jitem.id];
                            var _fieldsData = [];
                            $.each(_jitem.fieldsData, function (_m, _mitem) {
                                if (!_gird[_mitem.id] || _gird[_mitem.id].isLook == 1) {
                                    _fieldsData.push(_mitem);
                                    if (_gird[_mitem.id] && _gird[_mitem.id].isEdit != 1) {
                                        _mitem._isEdit = 1;
                                    }
                                }
                                else {
                                    _mitem.ishide = true;
                                }
                            });
                            _jitem.fieldsData = _fieldsData;
                        }
                        //else if (_jitem.type == 'upload') {
                        //    //if (isLook)
                        //        console.log(_jitem, formInfo.authorize);
                        //}
                    });
                });

                formInfo.girdCompontMap = $container.lrCustmerFormRender(formScheme.data);

                // 表单组件权限
                $.each(formInfo.authorize || {}, function (_field, _item) {
                    if (_field.indexOf('|') == -1) {
                        if (_item.isLook != 1) {// 如果没有查看权限就直接移除
                            $('#' + _field).parent().remove();
                            $('[name="' + _field + '"]').parents('.lr-form-item').remove();
                            $('[com-id="' + _field + '"]').remove();
                        }
                        else {
                            if (_item.isEdit != 1) {
                                $('#' + _field).attr('disabled', 'disabled');
                                $('#' + _field).unbind('click');
                                if ($('#' + _field).hasClass('lrUploader-wrap')) {
                                    $('#' + _field).lrUploaderAuth({ isUpload: false });
                                }
                                else if ($('#' + _field).hasClass('edui-default')) {
                                    var ue = $('#' + _field)[0].ue;
                                    setUeDisabled(ue);
                                }
                            }
                        }
                    }
                });

                formApi.loadFormData(formInfo, processId, formInfo.field, function (formData, _formInfo) {
                    $.each(formData, function (id, item) {
                        if (_formInfo.girdCompontMap[id]) {
                            var fieldMap = {};
                            $.each(_formInfo.girdCompontMap[id].fieldsData, function (id, girdFiled) {
                                if (girdFiled.field) {
                                    fieldMap[girdFiled.field.toLowerCase()] = girdFiled.field;
                                }
                            });
                            var rowDatas = [];
                            for (var i = 0, l = item.length; i < l; i++) {
                                var _point = {};
                                for (var _field in item[i]) {
                                    _point[fieldMap[_field]] = item[i][_field];
                                }
                                rowDatas.push(_point);
                            }
                            if (rowDatas.length > 0) {
                                _formInfo.isUpdate = true;
                            }
                            $('#' + _formInfo.girdCompontMap[id].id).jfGridSet('refreshdata', { rowdatas: rowDatas });
                        }
                        else {
                            if (item[0]) {
                                _formInfo.isUpdate = true;
                                $('#wfFormContainer').lrSetCustmerformData(item[0], id);
                            }
                        }
                    });
                    $.each(_formInfo.authorize || {}, function (_field, _item) {
                        if (_item.isLook == 1 && _item.isEdit != 1) {// 如果没有查看权限就直接移除
                            $('[name="' + _field + '"]').attr('disabled', 'disabled');
                        }
                    });
                    $('.flow-btn').show();
                });
            });
        },
        // 获取数据
        loadScheme: function (formId, callback) {
            learun.httpAsync('GET', top.$.rootUrl + '/LR_FormModule/Custmerform/GetFormData', { keyValue: formId }, function (data) {
                data && callback(data);
            });
        },
        loadFormData: function (formInfo, processId, processIdName, callback) {
            learun.httpAsync('GET', top.$.rootUrl + '/LR_FormModule/Custmerform/GetInstanceForm', { schemeInfoId: formInfo.formId, keyValue: processId, processIdName: processIdName }, function (data) {
                callback && callback(data, formInfo);
            });
        },

        // 验证表单数据完整性
        validForm: function (code, nwfForms) {// 操作码 create创建
            if (nwfForms.length > 0) {
                var form = nwfForms[0];
                if (form.type == '1') {// 自定义表单
                    if (!$.lrValidCustmerform()) {// 自定义表单
                        return false;
                    }
                }
                else {// 系统表单
                    if (formIframe.validForm && !formIframe.validForm(code)) {
                        return false;
                    }
                    else if (formIframe.page && formIframe.page.validForm && !formIframe.page.validForm(code)) {
                        return false;
                    }
                }
            }
            return true;
        },

        // 保存数据
        save: function (processId, nwfForms, callback) { 
            if (nwfForms.length > 0) {
                var form = nwfForms[0];
                if (form.type == '1') {// 自定义表单
                    var postData = {
                        schemeInfoId: form.formId,
                        processIdName: form.field
                    };
                    var formData = $('#wfFormContainer').lrGetCustmerformData();
                    if (form.isUpdate) {
                        postData.keyValue = processId;
                    }
                    formData[form.field] = processId;
                    postData.formData = JSON.stringify(formData);
                    $.lrSaveForm(top.$.rootUrl + '/LR_FormModule/Custmerform/SaveInstanceForm', postData, function (res) {
                        if (res.code == 200) {
                            form.isUpdate = true;
                            callback();
                        }
                        else {
                            learun.alert.error('表单数据保存失败');
                        }
                    });
                }
                else {// 系统表单
                    formIframe.save && formIframe.save(processId, function (res) { // 系统表单保存成功后需要将状态设置为更新状态（草稿并不会关闭页面）
                        if (res.code == 200) {
                            formIframe.isUpdate = true;
                            callback &&callback();
                        }
                        else {
                            learun.alert.error('表单数据保存失败');
                        }
                    });

                    formIframe.page && formIframe.page.save && formIframe.page.save(processId, function (res) { // 系统表单保存成功后需要将状态设置为更新状态（草稿并不会关闭页面）
                        if (res.code == 200) { 
                            formIframe.isUpdate = true; 
                            callback &&callback();
                        }
                        else {
                            learun.alert.error('表单数据保存失败');
                        }
                    });
                }
            }
        },

        systemFormLoad: function (iframeId, url, callback) {
            var _iframe = document.getElementById(iframeId);
            var _iframeLoaded = function () {
                formIframe = learun.iframe(iframeId, frames);
                formIframe.$ && callback(formIframe);
            };

            if (_iframe.attachEvent) {
                _iframe.attachEvent("onload", _iframeLoaded);
            } else {
                _iframe.onload = _iframeLoaded;
            }
            $('#' + iframeId).attr('src', top.$.rootUrl + url);
        },
    };

    // 设置富文本不可编辑
    function setUeDisabled(ue) {
        ue.ready(function () {
            ue.setDisabled();
        });
    }

})(jQuery, top.learun);