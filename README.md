# topics_tree



Пока что в в качестве примера, чтоб понять что нужно сделать (а то не понятно все равно) попробовал для "Политического раздела" расставить тэги по некоторым веткам (которые обновлялись в этом разделе за последние 2 года):

- есть список веток в виде .csv, в крайние столбцы tag1 tag2 tag3 на некоторые ветки  политического раздела добавлены тэги  : [main_topics.csv](https://github.com/normalized2/topics_tree/blob/master/main_topics.csv). Человек с ним работает и расставляет тэги.
- для того чтобы оценить что получается, как раскидываются ветки, вот для этого  понадобилось дерево [tree.md](https://github.com/normalized2/topics_tree/blob/master/tree.md) (составлено человеком), в котором тэги расставлены иерархически ручками.
- С помощью двух этих исходных файлов после проверки сгенерирован ([check.ipynb](https://github.com/normalized2/topics_tree/blob/master/check.ipynb)) пример view-шки, что получается: [topics_generated.md](https://github.com/normalized2/topics_tree/blob/master/topics_generated.md)

Вопросы и неясности:
- Что дальше-то? Что должно получиться в итоге? Правильное ли направление?
- Так как к ветке могут быть привязаны несколько тэгов, то ветка может одновременно попасть в несколько каталогов (Например [Донбасс - его жизнь и судьба](https://glav.su/forum/4/2658/) и к России и к Украине)
- К самим каталогам, например "Россия" может быть привязана ветка, но только одна. (добавить столбец в csv файл? или как?)
- Пока что в рамках раздела, в дереве, тэги уникальны. То есть тэг США в "Политическом разделе" может быть в дереве только  не более одного раза (а ведь можно придумать случаи, когда потребуется чтоб какой-то тэг в дереве встречался более одного раза)

А чтобы строить иерархию автоматически  без дерева, только на основе main_topics.csv (названия, тэгов, и, например, на основе текста первых двадцати сообщений и других данных), то нужно что-то типа [тематического моделирования](https://habrahabr.ru/company/yandex/blog/313340/) которое поддерживает динамику, или что-то еще.

Теперь насчет workflow:
если хотя бы на 50% направление верно (но после обсуждения), то можно брать .csv файл и пробовать дальше расставлять теги. Сам я все ветки расставить, конечно, не смогу (я о них и представления-то не имею, что там и кто там чего обсуждал или обсуждает), Особенно много топиков на "Пользовательских разделах" (половина, 800 из 1600) понятно что все не нужно и некоторые старые, но желательно охватить (так как потом возможно будет обучение, чтоб автоматически классифицировать документ). Начать, кмк, для примера нужно с двух разделов (чтоб учесть проблему общих тэгов и тем).
(И все равно, до конца не понимаю результат, и зачем все это нужно)
