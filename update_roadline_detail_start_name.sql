-- =====================================================
-- 根据站级信息管理更新线路走向信息管理的起点名称
-- =====================================================
-- 说明：
-- 1. 将站级信息管理表（dwd_roadline_stop_rel）中每个线路走向的第一个站级名称
--    更新到线路走向信息管理表（dwd_roadline_dtl）中的起点名称字段
-- 2. 根据 line_dtl_id 关联
-- 3. 取站序（level_id）最小的站级名称（level_name）作为起点名称
-- 4. 只更新站级信息管理表中存在对应站级数据的记录
-- =====================================================

-- 方式1：更新所有有站级数据的线路走向记录（推荐）
UPDATE gjgg_ai.dwd_roadline_dtl rd
SET start_stop_name = (
    SELECT rsr.level_name
    FROM gjgg_ai.dwd_roadline_stop_rel rsr
    WHERE rsr.line_dtl_id = rd.id
      AND rsr.level_id IS NOT NULL
      AND rsr.level_name IS NOT NULL
      AND rsr.delete_mark = 0
    ORDER BY rsr.level_id ASC
    LIMIT 1
)
WHERE EXISTS (
    SELECT 1
    FROM gjgg_ai.dwd_roadline_stop_rel rsr
    WHERE rsr.line_dtl_id = rd.id
      AND rsr.level_id IS NOT NULL
      AND rsr.level_name IS NOT NULL
      AND rsr.delete_mark = 0
);

-- 方式2：只更新起点名称为空的记录（更安全，避免覆盖已有数据）
-- UPDATE gjgg_ai.dwd_roadline_dtl rd
-- SET start_stop_name = (
--     SELECT rsr.level_name
--     FROM gjgg_ai.dwd_roadline_stop_rel rsr
--     WHERE rsr.line_dtl_id = rd.id
--       AND rsr.level_id IS NOT NULL
--       AND rsr.level_name IS NOT NULL
--       AND rsr.delete_mark = 0
--     ORDER BY rsr.level_id ASC
--     LIMIT 1
-- )
-- WHERE start_stop_name IS NULL
--   AND EXISTS (
--       SELECT 1
--       FROM gjgg_ai.dwd_roadline_stop_rel rsr
--       WHERE rsr.line_dtl_id = rd.id
--         AND rsr.level_id IS NOT NULL
--         AND rsr.level_name IS NOT NULL
--         AND rsr.delete_mark = 0
--   );

-- 方式3：使用窗口函数的方式（PostgreSQL/VastBase 支持）
-- UPDATE gjgg_ai.dwd_roadline_dtl rd
-- SET start_stop_name = subq.level_name
-- FROM (
--     SELECT DISTINCT ON (line_dtl_id)
--         line_dtl_id,
--         level_name
--     FROM gjgg_ai.dwd_roadline_stop_rel
--     WHERE level_id IS NOT NULL
--       AND level_name IS NOT NULL
--       AND delete_mark = 0
--     ORDER BY line_dtl_id, level_id ASC
-- ) subq
-- WHERE rd.id = subq.line_dtl_id;

-- =====================================================
-- 查询验证SQL（执行更新前可以先执行查看影响范围）
-- =====================================================
-- 查看将要更新的记录数量
-- SELECT COUNT(*) as update_count
-- FROM gjgg_ai.dwd_roadline_dtl rd
-- WHERE EXISTS (
--     SELECT 1
--     FROM gjgg_ai.dwd_roadline_stop_rel rsr
--     WHERE rsr.line_dtl_id = rd.id
--       AND rsr.level_id IS NOT NULL
--       AND rsr.level_name IS NOT NULL
--       AND rsr.delete_mark = 0
-- );

-- 查看更新前后的对比（执行更新前）
-- SELECT 
--     rd.id as detail_id,
--     rd.roadline_id,
--     r.line_name as 线路名称,
--     rd.updown as 上下行,
--     CASE WHEN rd.updown = 0 THEN '上行' ELSE '下行' END as 上下行名称,
--     rd.start_stop_name as 更新前起点名称,
--     (
--         SELECT rsr.level_name
--         FROM gjgg_ai.dwd_roadline_stop_rel rsr
--         WHERE rsr.line_dtl_id = rd.id
--           AND rsr.level_id IS NOT NULL
--           AND rsr.level_name IS NOT NULL
--           AND rsr.delete_mark = 0
--         ORDER BY rsr.level_id ASC
--         LIMIT 1
--     ) as 更新后起点名称,
--     (
--         SELECT MIN(rsr.level_id)
--         FROM gjgg_ai.dwd_roadline_stop_rel rsr
--         WHERE rsr.line_dtl_id = rd.id
--           AND rsr.level_id IS NOT NULL
--           AND rsr.delete_mark = 0
--     ) as 最小站序
-- FROM gjgg_ai.dwd_roadline_dtl rd
-- LEFT JOIN gjgg_ai.dwd_roadline r ON rd.roadline_id = r.id
-- WHERE EXISTS (
--     SELECT 1
--     FROM gjgg_ai.dwd_roadline_stop_rel rsr
--     WHERE rsr.line_dtl_id = rd.id
--       AND rsr.level_id IS NOT NULL
--       AND rsr.level_name IS NOT NULL
--       AND rsr.delete_mark = 0
-- )
-- ORDER BY r.line_name, rd.updown;

-- 查看没有站级数据的线路走向记录（这些记录不会被更新）
-- SELECT 
--     rd.id as detail_id,
--     rd.roadline_id,
--     r.line_name as 线路名称,
--     rd.updown as 上下行,
--     CASE WHEN rd.updown = 0 THEN '上行' ELSE '下行' END as 上下行名称,
--     rd.start_stop_name as 当前起点名称
-- FROM gjgg_ai.dwd_roadline_dtl rd
-- LEFT JOIN gjgg_ai.dwd_roadline r ON rd.roadline_id = r.id
-- WHERE NOT EXISTS (
--     SELECT 1
--     FROM gjgg_ai.dwd_roadline_stop_rel rsr
--     WHERE rsr.line_dtl_id = rd.id
--       AND rsr.level_id IS NOT NULL
--       AND rsr.level_name IS NOT NULL
--       AND rsr.delete_mark = 0
-- )
-- ORDER BY r.line_name, rd.updown;
