你是一个资深全栈工程师 + 产品型设计师。请为一个名为 Coffee Ninja 的产品做一个可运行的单页 demo，核心目标是演示这条链路：

onboarding → match → “wow this is relevant” → willing to talk

这是一个职业发展社群里的 matching 产品。重点不是完整系统，而是一个能在 1–2 分钟内让人看懂价值的 demo。

====================
产品目标
====================
用户进入后，完成 onboarding，系统立即展示 1–2 个高质量 match（可以是 fake data），每个 match 都要有：
1. clear why-match explanation
2. 个性化 prompt
3. Interested action

用户在看到 match 时要明显感受到：
- 为什么是这个人
- 我能从他/她这里学到什么
- 我为什么值得点 Interested

====================
必须实现的页面与流程
====================

1) Onboarding（真实交互）
- 做成一个简洁、现代、移动端友好的 onboarding flow
- 用户需要填写/选择以下信息：

A. I can help with（供给）
要求：具体、可交易、不要抽象
示例：
- 从 consulting 转 product
- 如何进 Stripe / Notion
- 从 IC 到 manager transition

B. I want help with（需求）
示例：
- 想进入 AI PM
- 如何做 career pivot
- 如何提升 interview 表现

C. Experience signals（可信度）
轻量即可，不要复制 LinkedIn
- 公司
- 职级
- years

D. Conversation style（可选）
- tactical
- strategic
- casual

- 输入方式优先用 chips / selectable tags / short form
- 不要长文本，不要复杂表单
- Onboarding 完成后，要立刻给用户一个“你已经可以被匹配了”的反馈

2) Matching
- 展示 1–2 个高质量 match
- 可以全部用 mock data，但必须看起来非常合理
- 每个 match 卡片必须包含：

a. Name / headline
b. Why this match
   用非常直观的结构展示：
   - You want → They did
   - They want → You have

c. Conversation prompt
   要具体，不要泛泛而谈
   例如：
   - Ask: what was hardest in the transition?
   - Ask: how did you evaluate moving from consulting to PM?

d. Interested action
   - 一个明显的按钮
   - 点了之后显示一个 warm intro / next step 的状态
   - 不需要真实发消息，但要让用户感受到“已经准备好谈了”

====================
Match 类型要求
====================
请同时支持并展示以下三种 match 类型，至少 demo 里要出现其中 2 种，最好 3 种都出现：

1. Give-first match
- A 能帮 B，但 B 不能明显帮 A
- 用于 mentor 型用户

2. Mutual exchange
- 双向都有价值
- 这是最优且最重要的 match 类型

3. Peer match
- 同 level + 相似目标
- 更像同行交流，而不是上下游请教

每个 match 要标注它属于哪一种类型。

====================
用户体验要求
====================
- 整体风格：简洁、克制、可信、高质量
- 重点是“relevant”，不是“feature-rich”
- 不要做成社交 feed
- 不要做成复杂 CRM
- 不要做成完整聊天系统
- 不要做 scheduling
- 不要做真正的推荐算法后端
- 不要做登录/注册流程
- 不要做数据库持久化
- 所有数据都可以先放在前端 mock state 里

====================
Onboarding 的产品逻辑
====================
Onboarding 不只是收集信息，而是为了让系统能做出高质量 match。

请把 onboarding 做得像一个“结构化价值交换表单”，而不是 LinkedIn profile：
- 供给和需求都必须被结构化
- Experience signals 只保留最少必要信息
- Conversation style 是加分项，不是主流程

Onboarding 完成后，立刻显示类似：
- “We found 2 people who seem highly relevant”
- “You can help others too”
- “Your profile is now matchable”

====================
Matching 的产品逻辑
====================
每个 match 的核心信息结构必须清晰：

You want:
- xxx

They did:
- xxx

They want:
- xxx

You have:
- xxx

再加上：
- Why this matters
- What to ask
- Interested

这里的目标不是展示人物简介，而是让用户理解：
“这个人值得我花 30 分钟聊。”

====================
数据要求
====================
请先自己设计一组合理的 mock users / matches，至少包括：
- 1 个从 consulting 转 product / AI PM 的人
- 1 个想学 growth / strategy 的人
- 1 个 peer 类型的同级别用户
- 1 个 give-first 类型的 mentor-like 用户

这些 mock profiles 必须看起来像真实社区里的成员，而不是泛泛模板。

====================
实现要求
====================
请优先生成一个可运行的前端 demo。

建议：
- 单页应用
- 清晰的状态流转
- 适当的动画/过渡
- 卡片式信息展示
- 视觉层次明确

如果你要做交互，优先保证：
- onboarding 一步步推进
- 完成后自动进入 match 页
- match 页逐个展示
- 点击 Interested 后显示正反馈

====================
验收标准
====================
这个 demo 完成后，应该满足：
1. 任何人 30 秒内能看懂产品在解决什么问题
2. onboarding 能让用户愿意填写
3. match 页面能让用户立刻理解为什么 relevant
4. 用户会觉得“这个人值得聊”
5. 整个 demo 不依赖后端也能完整讲故事

====================
输出要求
====================
请直接生成代码，并确保可以本地运行。
如果需要，请先搭好项目结构，然后实现页面、组件、mock data 和状态流转。
重点是产品体验，不是算法复杂度。
