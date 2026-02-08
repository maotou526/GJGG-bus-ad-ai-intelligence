-- =====================================================
-- 根据线路信息管理更新线路走向信息管理的线路长度
-- =====================================================
-- 说明：
-- 1. 将线路信息管理表（dwd_roadline）中的 line_length 字段
--    更新到线路走向信息管理表（dwd_roadline_dtl）中的 line_length 字段
-- 2. 只更新有对应关联关系的记录
-- 3. 只更新线路信息管理表中 line_length 不为空的记录
-- 4. 可选：只更新线路走向信息管理表中 line_length 为空或不同的记录
-- =====================================================

-- 方式1：更新所有关联的记录（如果线路信息管理表中有线路长度）
UPDATE gjgg_ai.dwd_roadline_dtl rd
SET line_length = r.line_length
FROM gjgg_ai.dwd_roadline r
WHERE rd.roadline_id = r.id
  AND r.line_length IS NOT NULL;

-- 方式2：只更新线路走向信息管理中线路长度为空的记录（推荐，更安全）
-- UPDATE gjgg_ai.dwd_roadline_dtl rd
-- SET line_length = r.line_length
-- FROM gjgg_ai.dwd_roadline r
-- WHERE rd.roadline_id = r.id
--   AND r.line_length IS NOT NULL
--   AND rd.line_length IS NULL;

-- 方式3：更新所有记录，即使线路走向信息管理中已有值（强制覆盖）
-- UPDATE gjgg_ai.dwd_roadline_dtl rd
-- SET line_length = r.line_length
-- FROM gjgg_ai.dwd_roadline r
-- WHERE rd.roadline_id = r.id
--   AND r.line_length IS NOT NULL
--   AND (rd.line_length IS NULL OR rd.line_length != r.line_length);

-- =====================================================
-- 查询验证SQL（执行更新前可以先执行查看影响范围）
-- =====================================================
-- 查看将要更新的记录数量
-- SELECT COUNT(*) as update_count
-- FROM gjgg_ai.dwd_roadline_dtl rd
-- INNER JOIN gjgg_ai.dwd_roadline r ON rd.roadline_id = r.id
-- WHERE r.line_length IS NOT NULL;

-- 查看更新前后的对比（执行更新前）
-- SELECT 
--     rd.id as detail_id,
--     rd.roadline_id,
--     r.line_name as 线路名称,
--     rd.line_length as 更新前长度,
--     r.line_length as 更新后长度,
--     rd.updown as 上下行
-- FROM gjgg_ai.dwd_roadline_dtl rd
-- INNER JOIN gjgg_ai.dwd_roadline r ON rd.roadline_id = r.id
-- WHERE r.line_length IS NOT NULL
-- ORDER BY r.line_name, rd.updown;
