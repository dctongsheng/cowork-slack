# Self-Harness 论文精华整理

> 论文：Self-Harness: Harnesses That Improve Themselves  
> arXiv: https://arxiv.org/abs/2606.09498  
> HTML: https://arxiv.org/html/2606.09498v1  
> 作者：Hangfan Zhang, Shao Zhang, Kangcong Li, Chen Zhang, Yang Chen, Yiqun Zhang, Lei Bai, Shuyue Hu  
> 提交日期：2026-06-08

## 1. 一句话总结

Self-Harness 的核心观点是：LLM agent 的能力不只由底层模型决定，还强烈依赖外层的 harness。论文提出让一个固定模型基于自己的失败轨迹，自动发现弱点、提出 harness 修改、再通过回归测试验证，从而把模型特定的失败模式转化为可执行、可审计的 harness 补丁。

更简洁地说：

```text
不是训练模型，而是让模型改进“包裹它的运行制度”。
```

## 2. 什么是 harness

论文里的 harness 不是单纯的 prompt，而是 agent 和环境之间的整套运行脚手架，包括：

- 系统提示词和行为约束
- 工具列表和工具调用策略
- 文件读写、shell 执行、编辑等工具接口
- 验证前检查规则
- 失败恢复策略
- 运行时预算、循环打断、重试纪律
- 子任务拆解、中间件、artifact 管理等结构性机制

所以 harness 可以理解为：

```text
模型本身 + harness = 一个真正可运行的 agent
```

论文强调，同一个模型换不同 harness，表现可能差很多；同一套 harness 放到不同模型上，也会暴露出不同失败模式。

## 3. 关键理解：不是一个模型永远只对应一套 harness

更准确的关系是：

```text
模型 + 任务类型 + 工具环境 + 验证标准 -> 适配后的 harness
```

也就是说，harness 是 model-specific 的，但不是脱离任务和环境独立存在的。实际工程里更合理的结构是：

```text
通用基础 harness
+ 模型专属行为补丁
+ 任务域专属规则
+ 工具/环境专属约束
```

Self-Harness 做的事情，就是自动发现这些“模型专属行为补丁”。

## 4. 论文解决的问题

当前很多 LLM agent 的 harness 主要靠人工手调：

- 模型 A 容易忘记写输出文件
- 模型 B 容易重复执行失败命令
- 模型 C 容易丢失 shell 环境变量
- 模型 D 对结构化工具返回内容处理不稳

如果每换一个模型都靠工程师重新调 prompt、工具策略和失败恢复规则，成本会越来越高。

Self-Harness 的目标是让 agent 参与改进自己的 harness：

```text
执行任务 -> 收集失败轨迹 -> 总结失败模式 -> 生成 harness 补丁 -> 回归验证 -> 接受或拒绝
```

这个过程不依赖更强的外部模型，也不修改底层模型参数。

## 5. Self-Harness 的三阶段循环

### 5.1 Weakness Mining：弱点挖掘

先用当前 harness 跑一批任务，记录完整执行轨迹和 verifier 结果。系统不是只看最后哪道题失败，而是分析失败背后的机制。

典型失败机制包括：

- 没有创建 verifier 要求的输出文件
- 发现线索后继续无效探索，最终超时
- shell 或编辑工具失败后没有恢复
- 反复执行同一类失败命令
- 环境变量、PATH、安装工具只在当前 shell session 生效
- 最终 artifact 被覆盖、删除或格式错误

这一步的重点是把孤立错误聚类成可修复的行为模式。

### 5.2 Harness Proposal：提出候选修改

模型根据失败模式提出若干候选 harness 修改。论文强调候选修改必须满足两个条件：

- 小而具体：绑定到某个明确失败机制
- 多样但受限：不要泛泛加一堆“请认真检查”的大段 prompt

候选修改可能落在不同 harness 表面上，例如：

- instruction
- tools
- verification guidance
- runtime policy
- middleware
- artifact handling policy

每个 proposal 都要说明：

- 要解决哪个失败模式
- 修改哪个 harness surface
- 预期改变什么执行行为
- 可能带来什么回归风险

### 5.3 Proposal Validation：回归验证

候选 harness 不会直接上线，而是重新跑 held-in 和 held-out 任务。接受规则很保守：

```text
至少提升一个 split，并且不能降低另一个 split。
```

如果一个修改只是在 held-in 上更好、held-out 上更差，或者只是总分上升但某个 split 回退，就会被拒绝。通过验证的修改会进入下一版 harness；失败 proposal 会保留记录，但不改变当前 harness。

这个设计让 harness 演化过程具备可审计性，而不是让模型随意改 prompt。

## 6. 实验设置

论文在 Terminal-Bench-2.0 上验证 Self-Harness。Terminal-Bench-2.0 是一个面向终端交互任务的 benchmark，agent 需要在容器环境中读写文件、执行命令、安装依赖、生成 artifact，并由确定性 verifier 判断是否完成任务。

实验设置要点：

- 原始 Terminal-Bench-2.0 有 89 个任务
- 论文使用固定的 64 个任务子集
- 排除依赖不稳定外部网页资源或需要多模态输入的任务
- 初始 harness 基于 DeepAgent，但刻意保持最小化
- 初始工具包括基础文件读写、文件编辑和 shell 执行
- 底层模型固定，只允许修改 harness

测试模型：

| 模型 | 说明 |
| --- | --- |
| MiniMax M2.5 | 托管 API |
| Qwen3.5-35B-A3B | 本地部署 |
| GLM-5 | OpenRouter 托管端点 |

## 7. 核心结果

Self-Harness 在三个模型上都带来了提升，并且 held-out 也提升，说明不是简单记住 held-in 失败样本。

| 模型 | Held-in 初始 | Held-in Self-Harness | Held-out 初始 | Held-out Self-Harness |
| --- | ---: | ---: | ---: | ---: |
| MiniMax M2.5 | 43.0% | 50.0% | 40.5% | 61.9% |
| Qwen3.5-35B-A3B | 15.1% | 36.0% | 23.8% | 38.1% |
| GLM-5 | 47.7% | 57.0% | 42.9% | 57.1% |

论文报告的相对提升：

- MiniMax M2.5：held-in +16%，held-out +53%
- Qwen3.5-35B-A3B：held-in +138%，held-out +60%
- GLM-5：held-in +20%，held-out +33%

最大绝对提升出现在 MiniMax 的 held-out split：从 40.5% 到 61.9%，提升 21.4 个百分点。

## 8. 不同模型学到的 harness 补丁不同

这是论文最有价值的部分：Self-Harness 不是给所有模型加同一段更长 prompt，而是针对不同模型的失败模式生成不同修改。

### 8.1 MiniMax M2.5

主要失败模式：

- 找到关键线索后继续探索
- 太晚创建必需输出文件
- 工具调用循环过长
- 结构化工具内容处理不够稳

保留下来的 harness 修改：

- 尽早识别并创建 required artifact
- 对结构化工具输出更谨慎
- 工具消息过多时触发重定向
- 避免开放式探索消耗完整预算

论文案例：在 `count-dataset-tokens` 任务中，初始 harness 下 agent 找到 metadata 线索后继续探索，最终超时且没有写 `/app/answer.txt`；修改后 agent 会计算结果、写入 `/app/answer.txt`，再读回验证。

### 8.2 Qwen3.5-35B-A3B

主要失败模式：

- 反复执行同类失败命令
- 文件编辑失败后陷入覆盖、重试、删除循环
- 工具错误后没有围绕最终 artifact 恢复
- 已生成的必需文件可能被删除

保留下来的 harness 修改：

- 依赖预检查
- 避免重复失败命令
- 触发 loop breaking
- 工具错误后执行 artifact-focused recovery
- 通过 middleware 在错误后提醒恢复必需产物

论文案例：在 `extract-elf` 任务中，初始 harness 下 agent 创建了 `/app/extract.js`，但在多次编辑失败后把它删除，导致 verifier 失败；修改后 harness 会在工具错误后提示 agent 恢复缺失 artifact，重新生成 extractor，验证 JSON 输出，并保留 `/app/extract.js`。

### 8.3 GLM-5

主要失败模式：

- shell session 之间环境设置不持久
- 工具安装、PATH 修改等没有跨命令保留
- 探索时间过长
- 在 sanity check 失败后仍然过早结束

保留下来的 harness 修改：

- 持久化工具安装和 PATH 修改
- 修改环境后验证工具可访问
- 长时间探索后切换到实现和测试
- 对外部下载和长命令进行更有界的阶段化操作

论文案例：在 `build-pov-ray` 任务中，初始 harness 消耗大量预算在长下载和失败检查上；修改后 agent 会更早验证外部资源、修复失败 sanity check，再完成任务。

## 9. 方法的工程价值

这篇论文对 agent 工程的启发大于单纯 benchmark 分数。

### 9.1 Prompt 不是唯一调优对象

很多 agent 失败不是模型完全不会，而是运行制度没有约束好：

- 什么时候停止探索
- 什么时候必须生成 artifact
- 工具失败后怎么恢复
- 如何避免重复失败动作
- 如何在最终验证前检查产物

这些问题更适合通过 harness policy、middleware、runtime guard、verification guidance 来解决。

### 9.2 Harness 应该有回归测试

论文把 harness 修改当成软件工程变更处理：

```text
提出 patch -> 跑回归 -> 通过才合并
```

这比“改一句 prompt 看感觉”更稳。对真实 agent 产品来说，应该维护：

- held-in failure set
- held-out regression set
- trace logger
- verifier
- harness patch history
- accept/reject 记录

### 9.3 模型适配应从失败轨迹出发

不要假设所有模型都需要同一套 best practice prompt。更合理的流程是：

```text
先跑任务
看失败轨迹
聚类失败机制
再写模型专属 harness 补丁
```

## 10. 可复现的最小实现思路

论文没有在 arXiv 页面直接给出官方 GitHub 仓库。可复现一个简化版 Self-Harness，可以基于以下组件：

- agent 框架：DeepAgents 或类似 agent harness
- benchmark：Terminal-Bench / 自己的任务集
- trace recorder：记录工具调用、stdout/stderr、文件状态、verifier 输出
- proposer：让同一个模型读失败 trace，生成 harness patch
- validator：在 held-in 和 held-out 上重跑候选 harness
- gate：执行非回退接受规则

最小伪代码：

```python
harness = initial_harness

for round_id in range(max_rounds):
    traces = run_tasks(model, harness, held_in_tasks)
    failures = select_failed_traces(traces)

    weakness_clusters = model.mine_weaknesses(failures)
    proposals = model.propose_harness_patches(weakness_clusters, harness)

    accepted = []
    for patch in proposals:
        candidate = apply_patch(harness, patch)
        result = evaluate(candidate, held_in_tasks, held_out_tasks)

        if improves_one_split_without_regressing_other(result):
            accepted.append(patch)

    if not accepted:
        break

    harness = merge_patches(harness, accepted)
```

## 11. 局限性

论文也有明显边界：

- 只验证了 Terminal-Bench-2.0 的终端任务场景
- 依赖可靠 verifier；没有 verifier 时很难判断 harness 是否真的变好
- 评估成本高，每个候选 harness 都要反复跑任务
- 接受规则只看 pass rate，真实生产环境还要考虑安全、成本、延迟、可解释性
- 自动生成的 harness patch 可能对 benchmark 有偏
- 不是开放式递归自我进化，而是受控、有限、可验证的 harness 优化

## 12. 我的结论

Self-Harness 最重要的贡献不是“模型能自我进化”这个口号，而是把 agent 改进落到了一个可工程化的层面：

```text
失败轨迹 -> 失败机制 -> harness 补丁 -> 回归验证 -> 受控合并
```

它说明很多 agent 能力问题可以通过外层运行制度修复，而不必每次都换更强模型或微调模型。对 Codex、Claude Code、OpenHands、DeepAgents 这类工具型 agent 来说，未来更可行的路线可能是：

```text
通用 agent 框架
+ 模型专属 harness patch
+ 任务域专属 harness patch
+ 持续回归验证
```

从这个角度看，一个模型确实应该有适配自己的 harness，但更完整的说法是：一个模型在某类任务、工具和验证环境下，需要一套经过失败轨迹校准的 harness。

