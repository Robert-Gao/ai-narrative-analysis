# 记录结构与边界示例

按任务选择字段，可增删。不生成无实际用途的空文件。关系以稳定 ID 连接；避免只能靠表格行号关联。

## 语料台账

`document_id, source_type, publisher, original_speaker, title, url_or_file, published_at, collected_at, language, genre, ai_scope, inclusion_reason, fulltext_status, duplicate_group, raw_text_path, cleaned_text_path`

不同日期未知时留空并说明，不能以采集日期替代发表日期。个人受访者使用去标识 ID；原始身份信息不放进可共享表。

## 编码本（适用于需要稳定编码规则的路径）

`code_id, label, construct, definition, unit, inclusion_rule, exclusion_rule, allowed_values, multilabel_rule, positive_example, boundary_example, theoretical_or_inductive_basis, version`

反思性主题分析改用解释备忘录和主题演变记录，不强制冻结上述编码本。

## 原文—判断记录

`document_id, segment_id, speaker, exact_quote, locator, code_id, evidence_status, brief_rationale, alternative_reading, review_status, coder_id, codebook_version`

- `locator`：段号、页码、时间戳或在指定版本中的字符位置。
- `evidence_status`：直接表达 / 语境推断 / 证据不足。
- `review_status`：模型建议 / 人工复核 / 保留争议等；未复核不得冒充人工确认。
- 引语必须与定位处一致；省略符号或翻译明确标注，保留原文。

## 多主体表达与关系记录

用于跨主体主张分析；普通单文本任务无需建立全部表。定义与判定规则见 [multi-actor-claims.md](multi-actor-claims.md)。

- 主体：`actor_id, actor_type, identity_evidence`；组织、角色和国家关联按表达时点记录。
- 表达：`occurrence_id, document_id, actor_id, event_id, argument_group_id, organization_at_time, speaking_capacity, country_link_and_basis, expression_mode, exact_quote, locator, claim_id, evidence_status, review_status`。
- 命题归并：`claim_id, occurrence_id, equivalence_basis, reviewer, review_status`；实质变义不并为同一命题。
- 关系：`relation_id, from_occurrence_id, to_occurrence_id, target_description, relation_type, target_match, evidence_quote, locator, temporal_basis, review_status`。方向为回应／转述表达指向被回应表达。
- 可选采用观察：`claim_id, outlet_id, event_window, eligibility_basis, observed_adoption, access_status`。未出现不是表达记录，也不证明主动拒绝。

关系目标未定位时保留描述，不虚构目标 ID。文件台账补充 `discovery_route, version, original_channel`，并保留发布者与发言者区别。

## 实验衔接表

`dimension, corpus_evidence_ids, construct_definition, manipulation, condition_id, stimulus_id, stimulus_version, controlled_features, possible_confounds, manipulation_check, primary_outcome, planned_contrast`

所有 `corpus_evidence_ids` 都应可追溯；纯构造设计留空并注明“研究者构造”，不伪造 ID。

## 合成示例：只用于理解边界

以下句子均为虚构训练材料，不是新闻、访谈或研究证据。

**A**：“公司称，新助手会替员工承担重复工作，但工会担心这会成为裁员的理由。”

应保留两个声音：公司提出辅助角色和收益；工会提出裁员风险。文章整体可呈现竞争性叙事，不能仅因转述公司话语就编码为媒体支持公司；更不能推断读者已经产生焦虑。

**B**：“这款 AI 真是天才，连日期都算错。”

字面正面词可能构成反讽。无语境时保留不确定；既不能按“天才”自动判积极，也不必据一句评价识别完整叙事。

**C**：“AI 投资今年增长。”

这句话至多提供主题与变化线索；不足以单独判定“技术救赎叙事”。现实增长是否属实还需要外部事实核查。

**D**：从 20 条便利抽取的评论中发现 12 条批评 AI。

可以报告该样本中批评表达的数量，不能报告“60% 公众反对 AI”，也不能据此说明某篇文章造成反对。

## 交付前自检

- 所有实质判断能否回到原文，是否区分说话者与作者立场？
- 框架、主题、叙事和情感是否被无理由地混为一谈？
- 类别是否容纳反例与混合，是否说明计数单位与分母？
- 方法名称是否与实际分析程序一致？
- 有没有把文本特征写成受众效果，把关联写成因果？
- 模型输出、合成示例、预试和正式数据是否明确分开？
- 待核实出处、访问缺失与人工复核状态是否如实记录？
