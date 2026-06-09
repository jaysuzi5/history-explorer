"""
Management command: seed_romanov
Creates the Romanov Dynasty era, 5 periods, 18 tsars, and succession relationships.
Idempotent — safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from explorer.models import Era, Period, Person, Relationship

ERA = {
    'name': 'Romanov Dynasty',
    'slug': 'romanov-dynasty',
    'tagline': "Russia's Imperial Age, 1613–1917",
    'summary': (
        'The Romanov dynasty ruled Russia for over three centuries, transforming a medieval '
        'tsardom into a vast empire stretching from the Baltic to the Pacific. From the '
        'election of Michael I in 1613 to the abdication of Nicholas II in 1917, eighteen '
        'rulers shaped the destiny of one of history\'s great powers.'
    ),
    'body': (
        '## Overview\n\n'
        'The Romanovs came to power in the aftermath of the [[time-of-troubles]], a period '
        'of civil war, famine, and foreign invasion that nearly destroyed the Russian state. '
        'The young Michael I, elected by the Zemsky Sobor in 1613, founded a dynasty that '
        'would endure for 304 years.\n\n'
        '## Transformation of Russia\n\n'
        'The dynasty\'s defining moment came under [[peter-i]], who between 1682 and 1725 '
        'dragged Russia into the European world by force of will — founding St. Petersburg, '
        'defeating Sweden in the Great Northern War, and proclaiming the Russian Empire. '
        'Subsequent rulers built upon this foundation, with [[catherine-ii]] extending the '
        'empire\'s borders and [[alexander-ii]] liberating the serfs.\n\n'
        '## The Fall\n\n'
        'The dynasty\'s end came swiftly. [[nicholas-ii]]\'s inability to manage the '
        'pressures of industrialization, war, and revolutionary politics led to his '
        'abdication in March 1917. The former tsar and his family were executed by '
        'Bolsheviks in Yekaterinburg on July 17, 1918, ending the dynasty forever.'
    ),
    'start_year': 1613,
    'end_year': 1917,
    'color_accent': '#8b1a1a',
    'icon': 'bi-shield-fill',
    'order': 1,
    'status': 'published',
}

PERIODS = [
    {
        'slug': 'early-romanovs',
        'name': 'Early Romanovs',
        'start_year': 1613,
        'end_year': 1682,
        'order': 1,
        'status': 'published',
        'summary': (
            'The founding generation restored order after the Time of Troubles. '
            'Michael I, Alexis I, and Feodor III consolidated Romanov rule, '
            'absorbed Left-Bank Ukraine, and reformed the Orthodox Church, '
            'setting the stage for Peter\'s revolution from above.'
        ),
    },
    {
        'slug': 'petrine-era',
        'name': 'Petrine Era',
        'start_year': 1682,
        'end_year': 1762,
        'order': 2,
        'status': 'published',
        'summary': (
            'Peter the Great\'s revolutionary Westernization transformed Russia into '
            'a European power. The era also encompasses the turbulent succession '
            'crises after his death — the Age of Palace Coups — in which five rulers '
            'came and went in less than four decades.'
        ),
    },
    {
        'slug': 'catherines-age',
        'name': "Catherine's Age",
        'start_year': 1762,
        'end_year': 1796,
        'order': 3,
        'status': 'published',
        'summary': (
            'Catherine the Great\'s thirty-four year reign represented the zenith of '
            'Enlightenment Russia. She extended the empire through the Partitions of Poland '
            'and conquest of Crimea, patronized science and the arts, and corresponded '
            'with Voltaire and Diderot while suppressing the Pugachev Rebellion.'
        ),
    },
    {
        'slug': 'nineteenth-century',
        'name': '19th Century Reform Era',
        'start_year': 1796,
        'end_year': 1881,
        'order': 4,
        'status': 'published',
        'summary': (
            'A century of tension between autocratic conservatism and the imperative '
            'to modernize. Alexander I\'s triumph over Napoleon was followed by Nicholas I\'s '
            'repression, then Alexander II\'s Great Reforms — culminating in his '
            'assassination on the eve of further concessions.'
        ),
    },
    {
        'slug': 'final-romanovs',
        'name': 'Final Romanovs',
        'start_year': 1881,
        'end_year': 1917,
        'order': 5,
        'status': 'published',
        'summary': (
            'The twilight of the dynasty. Alexander III\'s iron conservatism preserved '
            'stability at the cost of mounting tensions. His son Nicholas II\'s reign '
            'brought military humiliation, revolution, and ultimately the collapse of '
            'three centuries of Romanov rule.'
        ),
    },
]

TSARS = [
    {
        'name': 'Michael I',
        'slug': 'michael-i',
        'title': 'Tsar of All Russia',
        'period_slug': 'early-romanovs',
        'birth_year': 1596, 'death_year': 1645,
        'reign_start': 1613, 'reign_end': 1645,
        'summary': (
            'First Romanov tsar, elected at age 16 by the Zemsky Sobor following the '
            'chaos of the Time of Troubles. His reign restored stability and order to '
            'a Russia devastated by civil war and Polish-Swedish invasion.'
        ),
        'body': (
            '## Rise to Power\n\n'
            'Michael Romanov was barely sixteen when the Zemsky Sobor — an assembly of '
            'nobles, clergy, and townspeople — elected him tsar in February 1613. His '
            'selection was partly political: the Romanov family had ties to the old Rurikid '
            'dynasty through Ivan the Terrible\'s first wife, Anastasia Romanova, yet was '
            'not powerful enough to threaten the boyar elite.\n\n'
            '## Reign\n\n'
            'The early years were dominated by his father Filaret, who returned from Polish '
            'captivity in 1619 and served as co-ruler and Patriarch until his death in 1633. '
            'Together they rebuilt royal authority, replenished the treasury, and expelled '
            'foreign forces. The Stolbovo Peace (1617) with Sweden and the Deulino Armistice '
            '(1618) with Poland stabilized Russia\'s borders at the cost of significant territory.\n\n'
            '## Legacy\n\n'
            'Michael I\'s greatest achievement was survival — reestablishing the legitimacy '
            'of tsarist authority after the chaos of the Time of Troubles and founding a '
            'dynasty that would rule Russia for three centuries.'
        ),
    },
    {
        'name': 'Alexis I',
        'slug': 'alexis-i',
        'title': 'Tsar of All Russia',
        'period_slug': 'early-romanovs',
        'birth_year': 1629, 'death_year': 1676,
        'reign_start': 1645, 'reign_end': 1676,
        'summary': (
            'Known as "the Quietest," Alexis I oversaw the absorption of Left-Bank Ukraine '
            'under the Treaty of Pereyaslav and the traumatic Schism of the Russian Orthodox '
            'Church. His reign laid the administrative groundwork for Peter the Great\'s later reforms.'
        ),
        'body': (
            '## The "Quietest" Tsar\n\n'
            'Alexis Mikhailovich earned his epithet "the Quietest" (Tishaishy) not from '
            'passivity but from his deep religious piety and personal gentleness — qualities '
            'that concealed a capable and active ruler. He inherited a stable state from '
            'his father Michael and built significantly upon it.\n\n'
            '## The Raskol\n\n'
            'The defining crisis of his reign was the Church Schism (Raskol) of the 1650s. '
            'Patriarch Nikon\'s liturgical reforms — correcting Russian Orthodox texts to '
            'conform to Greek originals — split the Church. Those who refused the new rites, '
            'the Old Believers, faced persecution. The schism permanently fractured Russian '
            'Orthodoxy and drove millions underground.\n\n'
            '## Ukraine and Expansion\n\n'
            'In 1654, Alexis accepted the Cossack Hetmanate\'s oath under the Pereyaslav '
            'Agreement, incorporating Left-Bank Ukraine into Russia. This set the stage for '
            'centuries of Russo-Ukrainian entanglement. His reign also saw Stenka Razin\'s '
            'massive peasant revolt (1670–71), which was suppressed with brutal efficiency.\n\n'
            '## Administrative Legacy\n\n'
            'Alexis codified Russian law in the Sobornoye Ulozheniye of 1649, which bound '
            'the serfs permanently to the land. He also encouraged foreign technical experts '
            'and began cautious Westernization — trends his son Peter would radicalize.'
        ),
    },
    {
        'name': 'Feodor III',
        'slug': 'feodor-iii',
        'title': 'Tsar of All Russia',
        'period_slug': 'early-romanovs',
        'birth_year': 1661, 'death_year': 1682,
        'reign_start': 1676, 'reign_end': 1682,
        'summary': (
            'Despite his frail constitution, Feodor III abolished the mestnichestvo system '
            'of hereditary rank precedence, a significant modernizing reform. He died without '
            'a clear heir, triggering the Streltsy Uprising that brought Peter I to power.'
        ),
        'body': (
            '## A Brief Reign\n\n'
            'Feodor Alexeyevich ruled for only six years, hampered throughout by severe '
            'ill health. Yet his brief reign produced one genuinely important reform: the '
            'abolition of mestnichestvo in 1682.\n\n'
            '## Abolition of Mestnichestvo\n\n'
            'Mestnichestvo was an intricate system under which noble families competed for '
            'government and military appointments based on the relative rank of their '
            'ancestors. This strangled military efficiency and administrative flexibility. '
            'Feodor\'s abolition of the system — and the burning of the registers that '
            'recorded ancestral precedence — was a genuine modernization that anticipated '
            'Peter the Great\'s meritocratic reforms.\n\n'
            '## Succession Crisis\n\n'
            'When Feodor died childless in April 1682, a bitter succession struggle broke '
            'out between factions supporting his half-brothers: the feeble Ivan V (backed '
            'by the Miloslavsky clan) and the young Peter (backed by the Naryshkins). '
            'The Streltsy militia\'s uprising settled matters by making both boys co-tsars, '
            'with their sister Sophia as regent.'
        ),
    },
    {
        'name': 'Ivan V',
        'slug': 'ivan-v',
        'title': 'Co-Tsar of All Russia',
        'period_slug': 'early-romanovs',
        'birth_year': 1666, 'death_year': 1696,
        'reign_start': 1682, 'reign_end': 1696,
        'summary': (
            'Mentally and physically infirm, Ivan V served as nominal co-tsar alongside '
            'his half-brother Peter. Real authority rested first with their sister Sophia '
            'and later with Peter alone. Ivan V exercised no actual power throughout his reign.'
        ),
        'body': (
            '## The Shadow Tsar\n\n'
            'Ivan Alexeyevich was by all accounts unable to rule. Contemporary accounts '
            'describe him as nearly blind, slow-witted, and barely able to stand. He was '
            'placed on the throne alongside the ten-year-old Peter primarily to legitimize '
            'the Miloslavsky faction\'s power.\n\n'
            '## Regency of Sophia\n\n'
            'Their sister Sophia Alexeyevna served as regent from 1682 to 1689, effectively '
            'governing Russia during this period. When Peter came of age and removed Sophia '
            'to a convent in 1689, Ivan remained a figurehead until his death in 1696.\n\n'
            '## Legacy\n\n'
            'Ivan V\'s main historical significance is dynastic: his daughter Anna would '
            'later rule Russia as Empress Anna (1730–1740), and through her the senior '
            'Romanov line continued even as Peter\'s direct descendants died out.'
        ),
    },
    {
        'name': 'Peter I',
        'slug': 'peter-i',
        'title': 'Emperor of All Russia',
        'period_slug': 'petrine-era',
        'birth_year': 1672, 'death_year': 1725,
        'reign_start': 1682, 'reign_end': 1725,
        'summary': (
            'Peter the Great fundamentally transformed Russia into a major European power '
            'through sweeping Westernization reforms, the founding of St. Petersburg, and '
            'victory in the Great Northern War. He assumed the title Emperor and is '
            'considered the founder of modern Russia.'
        ),
        'body': (
            '## The Reformer\n\n'
            'Peter I Alexeyevich stands as one of history\'s most transformative rulers. '
            'In a reign spanning over four decades, he turned an isolated, largely medieval '
            'state into a major European power — by sheer force of will, often literally '
            'dragging Russia into the modern world.\n\n'
            '## The Grand Embassy (1697–98)\n\n'
            'Peter\'s formative experience was his incognito tour of Western Europe — '
            'traveling as "Peter Mikhailov" to study shipbuilding in Holland and England, '
            'visiting factories and arsenals. He returned determined to Westernize Russia '
            'at any cost. He forced nobles to shave their beards, ordered Western dress, '
            'and reformed the calendar.\n\n'
            '## The Great Northern War\n\n'
            'Peter\'s greatest military achievement was the defeat of Sweden under Charles XII '
            'in the Great Northern War (1700–1721). After the humiliating defeat at Narva '
            'in 1700, Peter rebuilt his army on Western lines. The decisive victory at '
            'Poltava (1709) broke Swedish power and gave Russia access to the Baltic.\n\n'
            '## St. Petersburg\n\n'
            'In 1703, on land newly captured from Sweden, Peter founded his "window to Europe" '
            '— St. Petersburg. Built on swamps at enormous human cost, the city became '
            'Russia\'s new capital and a showcase of European architecture and culture.\n\n'
            '## Legacy\n\n'
            'Peter\'s reforms — a Western-style military, a modernized civil service, '
            'the subordination of the Church to the state, the founding of the Academy '
            'of Sciences — permanently altered Russia\'s trajectory. He died in 1725 '
            'without naming a successor, triggering decades of dynastic instability.'
        ),
    },
    {
        'name': 'Catherine I',
        'slug': 'catherine-i',
        'title': 'Empress of All Russia',
        'period_slug': 'petrine-era',
        'birth_year': 1684, 'death_year': 1727,
        'reign_start': 1725, 'reign_end': 1727,
        'summary': (
            'A Lithuanian peasant woman who became Peter the Great\'s companion and later '
            'empress. Catherine I was Russia\'s first female ruler, though real power during '
            'her brief reign lay with Prince Menshikov and the Supreme Privy Council.'
        ),
        'body': (
            '## From Peasant to Empress\n\n'
            'Martha Skavronskaya was born a Lithuanian peasant, became a laundress, and was '
            'captured during the Great Northern War. She caught Peter\'s attention, converted '
            'to Orthodoxy as "Catherine," and became his companion, then his wife in 1712. '
            'Peter publicly crowned her empress in 1724 — an extraordinary elevation.\n\n'
            '## Reign\n\n'
            'When Peter died in January 1725 without naming an heir, Menshikov and the '
            'guards regiments secured the throne for Catherine. Her two-year reign was '
            'largely ceremonial; the Supreme Privy Council, dominated by Menshikov, '
            'held actual power. She founded the Russian Academy of Sciences and sent '
            'Vitus Bering on his first Siberian expedition.\n\n'
            '## Legacy\n\n'
            'Catherine I established the precedent of female rule in Russia — a precedent '
            'that would see women occupy the throne for most of the next century.'
        ),
    },
    {
        'name': 'Peter II',
        'slug': 'peter-ii',
        'title': 'Emperor of All Russia',
        'period_slug': 'petrine-era',
        'birth_year': 1715, 'death_year': 1730,
        'reign_start': 1727, 'reign_end': 1730,
        'summary': (
            'Peter the Great\'s grandson who ascended the throne at age 11 and died of '
            'smallpox at 14, just before his planned wedding. His short reign saw Moscow '
            'briefly reclaim the capital status and marked the end of Peter the Great\'s '
            'direct male line.'
        ),
        'body': (
            '## The Boy Emperor\n\n'
            'Peter Alexeyevich was the son of Peter the Great\'s executed son Alexis. '
            'At age 11, with Menshikov\'s backing, he became emperor. Menshikov initially '
            'dominated the boy, even betrothing him to his daughter — but the Dolgorukov '
            'clan outmaneuvered him, had Menshikov exiled to Siberia, and moved the court '
            'to Moscow.\n\n'
            '## Brief Reign and Death\n\n'
            'The capital was moved back to Moscow in 1728, and Peter II showed signs of '
            'enjoying the hunt more than governance. Before he could marry the Dolgorukov '
            'candidate, he died of smallpox in January 1730, aged 14. With him died the '
            'last direct male descendant of Peter the Great.\n\n'
            '## Significance\n\n'
            'His death triggered a constitutional crisis. The Supreme Privy Council '
            'attempted to limit autocratic power before offering the throne to Anna of '
            'Courland — an experiment in limited monarchy that Anna promptly dismantled.'
        ),
    },
    {
        'name': 'Anna',
        'slug': 'anna',
        'title': 'Empress of All Russia',
        'period_slug': 'petrine-era',
        'birth_year': 1693, 'death_year': 1740,
        'reign_start': 1730, 'reign_end': 1740,
        'summary': (
            'Duchess of Courland whose reign was marked by heavy German influence — '
            'a period Russians called the Bironovshchina. She moved the capital back '
            'to St. Petersburg and continued Petrine Westernization while relying '
            'heavily on her Baltic German favorite, Ernst Johann von Biron.'
        ),
        'body': (
            '## The Conditions Rejected\n\n'
            'Anna, daughter of Ivan V and niece of Peter the Great, was invited to the '
            'throne with conditions that would have limited autocratic power. She initially '
            'signed but, finding broad noble support for autocracy, tore up the conditions '
            'and crushed the Supreme Privy Council that had imposed them.\n\n'
            '## Bironovshchina\n\n'
            'Anna\'s reign is remembered for the dominance of Ernst Johann von Biron, '
            'her Courland favorite, who effectively co-ruled with her. Germans occupied '
            'many key government positions. Russians resented this foreign influence so '
            'deeply that the era became synonymous with his name — the Bironovshchina.\n\n'
            '## The Secret Chancellery\n\n'
            'Anna revived and greatly expanded the Secret Chancellery, a feared instrument '
            'of political repression. Thousands were exiled to Siberia during her reign. '
            'Despite this, she maintained Peter\'s Westernizing reforms and built up the '
            'Russian military significantly.'
        ),
    },
    {
        'name': 'Ivan VI',
        'slug': 'ivan-vi',
        'title': 'Emperor of All Russia',
        'period_slug': 'petrine-era',
        'birth_year': 1740, 'death_year': 1764,
        'reign_start': 1740, 'reign_end': 1741,
        'summary': (
            'Proclaimed tsar at two months old, Ivan VI was deposed by Elizabeth after '
            'just fourteen months. He spent his entire life in captivity, never knowing '
            'freedom, and was killed in 1764 during a failed attempt to restore him to power.'
        ),
        'body': (
            '## The Infant Tsar\n\n'
            'Ivan Antonovich, great-grandson of Ivan V, was proclaimed emperor at two '
            'months old when Anna died in October 1740. His mother Anna Leopoldovna '
            'served as regent, but Biron initially maintained influence until he was '
            'overthrown in a palace coup.\n\n'
            '## Deposition\n\n'
            'In November 1741, Peter the Great\'s daughter Elizabeth staged a coup with '
            'the Preobrazhensky Guards, deposing the toddler emperor. Ivan was imprisoned '
            'and his parents exiled to Siberia.\n\n'
            '## Life in Prison\n\n'
            'Ivan VI spent the next twenty-three years in increasingly harsh imprisonment, '
            'first in Riga, then Kholmogory, and finally in the Shlisselburg Fortress. '
            'Kept in isolation, he grew up barely educated and apparently mentally disturbed. '
            'In 1764, an officer named Mirovich tried to free him; guards, acting on '
            'standing orders, killed the prisoner rather than allow his release. '
            'He was 23 years old and had never known a single day of freedom.'
        ),
    },
    {
        'name': 'Elizabeth',
        'slug': 'elizabeth',
        'title': 'Empress of All Russia',
        'period_slug': 'petrine-era',
        'birth_year': 1709, 'death_year': 1762,
        'reign_start': 1741, 'reign_end': 1762,
        'summary': (
            'Daughter of Peter the Great who seized power in a coup. Her twenty-year '
            'reign saw Russia\'s cultural flowering: the founding of Moscow University, '
            'the construction of the Winter Palace, and Russian victories in the '
            'Seven Years\' War against Prussia.'
        ),
        'body': (
            '## The Coup of 1741\n\n'
            'Elizabeth Petrovna had lived in semi-retirement during Anna\'s reign, '
            'carefully staying out of politics. In November 1741, she appeared before '
            'the Preobrazhensky Guards regiment and promised them glory and reward. '
            'They marched on the Winter Palace. Ivan VI was arrested without bloodshed.\n\n'
            '## Cultural Achievements\n\n'
            'Elizabeth\'s reign was a golden age of Russian culture. Mikhail Lomonosov '
            'founded Moscow University in 1755. Bartolomeo Rastrelli built the Winter '
            'Palace and the Smolny Cathedral in the exuberant Elizabethan Baroque style. '
            'Russian literature and court culture flourished.\n\n'
            '## The Seven Years\' War\n\n'
            'Russia entered the Seven Years\' War in 1756 against Prussia. By 1760, '
            'Russian forces had occupied Berlin. Frederick the Great was near collapse '
            'when Elizabeth died in January 1762 — prompting her nephew Peter III to '
            'immediately make peace with Prussia, squandering the victory.\n\n'
            '## Personal Rule\n\n'
            'Elizabeth never married officially (though she may have contracted a '
            'morganatic marriage) and had no direct heirs. She chose her nephew '
            'Peter of Holstein-Gottorp as her successor — a choice that would '
            'prove fateful.'
        ),
    },
    {
        'name': 'Peter III',
        'slug': 'peter-iii',
        'title': 'Emperor of All Russia',
        'period_slug': 'catherines-age',
        'birth_year': 1728, 'death_year': 1762,
        'reign_start': 1762, 'reign_end': 1762,
        'summary': (
            'A German prince and ardent admirer of Frederick the Great who alienated '
            'the Russian military by withdrawing from the victorious Seven Years\' War. '
            'His six-month reign ended when his wife Catherine organized a coup; '
            'he died shortly after abdication.'
        ),
        'body': (
            '## An Unlikely Tsar\n\n'
            'Karl Peter Ulrich of Holstein-Gottorp had been raised in Germany and spoke '
            'poor Russian. His admiration for Frederick the Great bordered on worship, '
            'which made him deeply unpopular with Russian officers who had been fighting '
            'Prussia for years.\n\n'
            '## The Peace with Prussia\n\n'
            'Peter\'s most consequential — and most resented — act was withdrawing Russia '
            'from the Seven Years\' War immediately upon taking the throne, returning all '
            'Russian conquests to Frederick without compensation. The Russian officer corps '
            'was furious.\n\n'
            '## The Coup\n\n'
            'In June 1762, after just six months on the throne, Peter\'s wife Catherine '
            'led the guards regiments in a coup. Peter abdicated and was sent to '
            'Ropsha under guard. Eight days later he was dead — officially from "hemorrhoidal '
            'colic," more probably at the hands of his captors.\n\n'
            '## Positive Acts\n\n'
            'Peter III is not entirely without credit: he abolished the Secret Chancellery '
            'and issued the Manifesto on the Freedom of the Nobility (1762), freeing the '
            'nobility from compulsory state service — one of the most significant social '
            'reforms of the century, though Catherine took the credit for his reign.'
        ),
    },
    {
        'name': 'Catherine II',
        'slug': 'catherine-ii',
        'title': 'Empress of All Russia',
        'period_slug': 'catherines-age',
        'birth_year': 1729, 'death_year': 1796,
        'reign_start': 1762, 'reign_end': 1796,
        'summary': (
            'Catherine the Great deposed her husband Peter III and became one of Russia\'s '
            'most capable rulers. She extended the empire through the Partitions of Poland '
            'and conquest of Crimea, patronized the Enlightenment, and suppressed '
            'the massive Pugachev Rebellion of 1773–75.'
        ),
        'body': (
            '## The German Princess\n\n'
            'Sophie of Anhalt-Zerbst arrived in Russia at age 14 to marry the heir to '
            'the throne. She threw herself into learning Russian, converted to Orthodoxy, '
            'and became Catherine. Her marriage to the future Peter III was miserable, '
            'but she cultivated allies, read Voltaire and Montesquieu, and waited.\n\n'
            '## Coup and Consolidation\n\n'
            'Within a year of Peter III\'s accession, Catherine organized her coup. '
            'The Orlov brothers and Grigory Potemkin (then a young officer) were among '
            'her key supporters. She ruled for thirty-four years — longer than any '
            'other Romanov before or after.\n\n'
            '## Enlightened Despotism\n\n'
            'Catherine corresponded with Voltaire, Diderot, and d\'Alembert. She wrote '
            'the Nakaz — an "Instruction" to a Legislative Commission drawing on '
            'Enlightenment principles — and convened the Commission in 1767. The '
            'practical results were limited, but the intellectual engagement was real.\n\n'
            '## Imperial Expansion\n\n'
            'Under Catherine, Russia absorbed Crimea (1783), parts of Poland in the '
            'three Partitions (1772, 1793, 1795), and new territories along the Black Sea. '
            'Her general Alexander Suvorov was one of history\'s greatest battlefield commanders.\n\n'
            '## The Pugachev Rebellion\n\n'
            'From 1773 to 1775, Yemelyan Pugachev led the largest peasant uprising in '
            'Russian history, proclaiming himself Peter III and promising freedom to serfs. '
            'The rebellion was eventually crushed, but it shocked Catherine into abandoning '
            'her earlier liberal impulses and hardening serfdom further.\n\n'
            '## Legacy\n\n'
            'Catherine the Great left Russia larger, stronger, and culturally richer. '
            'She founded the Hermitage Museum, reformed provincial administration, and '
            'established Russia as an undeniable great power. Her personal life — '
            'numerous favorites including Potemkin — scandalized Europe but never '
            'distracted her from governance.'
        ),
    },
    {
        'name': 'Paul I',
        'slug': 'paul-i',
        'title': 'Emperor of All Russia',
        'period_slug': 'nineteenth-century',
        'birth_year': 1754, 'death_year': 1801,
        'reign_start': 1796, 'reign_end': 1801,
        'summary': (
            'Catherine\'s estranged son whose erratic and authoritarian rule reversed '
            'many of his mother\'s policies. He was strangled by palace conspirators '
            'in 1801 in a coup almost certainly known in advance by his son Alexander.'
        ),
        'body': (
            '## Catherine\'s Son\n\n'
            'Paul I had a miserable relationship with his mother. Raised by Empress '
            'Elizabeth, he barely knew Catherine, who excluded him from government. '
            'When he finally came to power at 42, he seemed determined to reverse '
            'everything his mother had done.\n\n'
            '## Reign\n\n'
            'Paul reversed Catherine\'s foreign alliances, alienated the nobility by '
            'reimposing service obligations, introduced unpredictable military discipline '
            'based on Prussian models he admired, and issued the Pavlovian Laws of '
            'Succession (1797) — establishing male primogeniture, ending the era of '
            'palace coups that had destabilized Russia since Peter the Great\'s death.\n\n'
            '## The Coup\n\n'
            'Paul\'s unpredictability made enemies everywhere. A group of nobles, '
            'with the knowledge (if not the blessing) of his son Alexander, entered '
            'his bedroom at the Mikhailovsky Castle on the night of March 23, 1801 '
            'and strangled him with a scarf. Alexander, who became Emperor Alexander I '
            'the following day, carried the guilt of his father\'s murder for the rest '
            'of his life.\n\n'
            '## Redeeming Acts\n\n'
            'Paul passed the Pauline Laws of Succession, ensuring stable male-line '
            'inheritance and preventing future palace coups. He also proclaimed '
            'Russia\'s neutrality and experimented briefly with alignment with Napoleon — '
            'a foreign policy reversal that contributed to his assassination.'
        ),
    },
    {
        'name': 'Alexander I',
        'slug': 'alexander-i',
        'title': 'Emperor of All Russia',
        'period_slug': 'nineteenth-century',
        'birth_year': 1777, 'death_year': 1825,
        'reign_start': 1801, 'reign_end': 1825,
        'summary': (
            'The "Blessed" tsar who repelled Napoleon\'s 1812 invasion and led the '
            'allied coalition to Paris in 1814, reshaping European order at the Congress '
            'of Vienna. He began as a liberal reformer but ended his reign as a '
            'conservative mystic.'
        ),
        'body': (
            '## Liberal Beginnings\n\n'
            'Alexander I came to power promising reform. Influenced by La Harpe, his '
            'Swiss tutor, and his friend Mikhail Speransky, he contemplated constitutional '
            'government and the abolition of serfdom. Some reforms were enacted — '
            'universities founded, government ministries reorganized — but fundamental '
            'change never came.\n\n'
            '## Napoleon and 1812\n\n'
            'Alexander\'s defining moment came with Napoleon\'s Grande Armée invasion '
            'of Russia in June 1812. Rather than submit, Russia retreated, allowing the '
            'French to occupy Moscow — which burned, perhaps deliberately. Faced with '
            'winter, partisan resistance, and no peace offer from Alexander, Napoleon '
            'began his catastrophic retreat. Six hundred thousand entered Russia; '
            'perhaps one hundred thousand left.\n\n'
            '## The Congress of Vienna\n\n'
            'Alexander led the allied coalition that entered Paris in March 1814 and '
            'helped redraw Europe at the Congress of Vienna (1814–15). He proposed '
            'the Holy Alliance — a quasi-mystical pact among Christian monarchs to '
            'govern by Christian principles. His later years were marked by growing '
            'religious mysticism and political conservatism.\n\n'
            '## The Mysterious Death\n\n'
            'Alexander died in November 1825 in Taganrog of typhus — or did he? '
            'A persistent legend holds that he faked his death to become the hermit '
            'Fyodor Kuzmich, living in Siberia until 1864. No serious historian '
            'accepts this, but the story endured and his death without a clear '
            'succession plan triggered the Decembrist Revolt.'
        ),
    },
    {
        'name': 'Nicholas I',
        'slug': 'nicholas-i',
        'title': 'Emperor of All Russia',
        'period_slug': 'nineteenth-century',
        'birth_year': 1796, 'death_year': 1855,
        'reign_start': 1825, 'reign_end': 1855,
        'summary': (
            'His reign began by crushing the Decembrist Revolt and ended in the '
            'humiliating Crimean War. Nicholas I championed autocracy, orthodoxy, and '
            'Russian nationalism, earning the name "the Gendarme of Europe" for '
            'suppressing liberal movements across the continent.'
        ),
        'body': (
            '## The Decembrist Test\n\n'
            'Nicholas I came to the throne on December 14, 1825 — the same day as '
            'the Decembrist Revolt, an uprising of reform-minded officers who wanted '
            'a constitutional monarchy. Nicholas personally supervised the suppression '
            'and sentencing. Five leaders were hanged; over a hundred were exiled to '
            'Siberia. The experience hardened his autocratic instincts.\n\n'
            '## Official Nationality\n\n'
            'Nicholas\'s governing philosophy was captured in the doctrine of "Official '
            'Nationality": Orthodoxy, Autocracy, and Nationality. Universities were '
            'regulated, censorship tightened, and the Third Section (secret police) '
            'created. He was called the "Gendarme of Europe" for helping Austria crush '
            'the Hungarian revolution of 1848.\n\n'
            '## The Crimean Catastrophe\n\n'
            'Nicholas overestimated Russia\'s military strength and underestimated British '
            'and French determination. When Russia invaded the Ottoman Danubian '
            'Principalities in 1853, triggering the Crimean War, the conflict exposed '
            'Russia\'s backwardness. The siege of Sevastopol (1854–55) became a '
            'national trauma. Nicholas died in February 1855, his illusions destroyed.\n\n'
            '## Contradictions\n\n'
            'Nicholas was not without merit. He codified Russian law under Speransky, '
            'stabilized the currency, and oversaw significant industrial beginnings. '
            'He privately acknowledged serfdom was evil while refusing to abolish it, '
            'fearing social chaos. He left that task — and its consequences — to his son.'
        ),
    },
    {
        'name': 'Alexander II',
        'slug': 'alexander-ii',
        'title': 'Emperor of All Russia',
        'period_slug': 'nineteenth-century',
        'birth_year': 1818, 'death_year': 1881,
        'reign_start': 1855, 'reign_end': 1881,
        'summary': (
            'The Tsar-Liberator who emancipated 23 million serfs in 1861, the most '
            'sweeping social reform in Russian history. He survived multiple assassination '
            'attempts but was killed by a revolutionary bomb in St. Petersburg '
            'on March 13, 1881.'
        ),
        'body': (
            '## The Great Reforms\n\n'
            'The Crimean defeat convinced Alexander II that Russia must modernize. '
            'His response was the most sweeping program of reform in Russian history. '
            'The Emancipation of the Serfs (1861) freed approximately 23 million people — '
            'though the redemption payment terms left many peasants deeply indebted. '
            'Judicial reform (1864) created independent courts and trial by jury. '
            'Zemstvo reform created elected local assemblies. Military reform introduced '
            'universal conscription.\n\n'
            '## Assassination Attempts\n\n'
            'As reforms proved insufficient for radicals and too radical for conservatives, '
            'Alexander became a target. He survived at least six assassination attempts: '
            'a shot in Paris (1867), a train derailment attempt (1879), a Winter Palace '
            'explosion (1880). The People\'s Will organization was determined to kill him.\n\n'
            '## The Killing\n\n'
            'On March 13, 1881, Alexander\'s carriage was hit by a bomb in St. Petersburg. '
            'He survived the first blast but stepped out to check on the wounded. A second '
            'bomb thrown by Ignacy Hryniewiecki killed them both. Alexander died hours later.\n\n'
            '## Bitter Irony\n\n'
            'On the very day of his assassination, Alexander had approved a consultative '
            'assembly plan that might have put Russia on a constitutional path. His son '
            'Alexander III immediately abandoned it.'
        ),
    },
    {
        'name': 'Alexander III',
        'slug': 'alexander-iii',
        'title': 'Emperor of All Russia',
        'period_slug': 'final-romanovs',
        'birth_year': 1845, 'death_year': 1894,
        'reign_start': 1881, 'reign_end': 1894,
        'summary': (
            'Hardened by his father\'s assassination, Alexander III was a staunch '
            'reactionary who reversed liberal reforms and promoted Russification. '
            'He oversaw rapid industrialization under Finance Minister Witte, maintaining '
            'stability at the cost of storing up enormous social tensions.'
        ),
        'body': (
            '## Reaction\n\n'
            'Alexander III witnessed his father\'s death and drew one conclusion: liberalism '
            'kills. He immediately issued the Manifesto on the Inviolability of Autocracy, '
            'abandoned his father\'s proposed constitutional assembly, and executed the '
            'People\'s Will conspirators — including the pregnant Sophia Perovskaya.\n\n'
            '## Counter-Reforms\n\n'
            'Alexander systematically reversed the Great Reforms. Zemstvo powers were '
            'curtailed. University autonomy was abolished. Judicial independence was '
            'reduced. The "Temporary Regulations" of 1881 gave police sweeping powers '
            'of administrative exile without trial. Jews were confined to the Pale of '
            'Settlement and subjected to violent pogroms.\n\n'
            '## Russification\n\n'
            'Alexander pursued aggressive Russification of Finland, Poland, and the '
            'Baltic provinces, replacing local languages with Russian in schools and '
            'government. This created lasting resentments in the empire\'s borderlands.\n\n'
            '## Industrial Progress\n\n'
            'Despite his conservatism, Alexander III oversaw dramatic economic development '
            'under Finance Minister Sergei Witte. The Trans-Siberian Railway was begun '
            'in 1891. Foreign investment flooded in. Russia industrialized rapidly — '
            'creating the urban working class that would fuel the revolutions of 1905 '
            'and 1917.\n\n'
            '## Stability and Legacy\n\n'
            'Alexander III died of kidney disease at 49. His Russia was externally stable '
            'but internally pressurized. He left his son Nicholas II a throne that looked '
            'solid but sat on a volcano.'
        ),
    },
    {
        'name': 'Nicholas II',
        'slug': 'nicholas-ii',
        'title': 'Emperor of All Russia',
        'period_slug': 'final-romanovs',
        'birth_year': 1868, 'death_year': 1918,
        'reign_start': 1894, 'reign_end': 1917,
        'summary': (
            'The last Romanov tsar whose reign was marked by defeat in the Russo-Japanese '
            'War, the 1905 Revolution, World War I, and Rasputin\'s influence at court. '
            'He abdicated in March 1917 and was executed with his entire family by '
            'Bolsheviks in Yekaterinburg on July 17, 1918.'
        ),
        'body': (
            '## An Unprepared Ruler\n\n'
            'Nicholas II inherited the throne at 26 when his father died unexpectedly. '
            'He reportedly told his cousin Sandro: "What is going to happen to me and '
            'all of Russia? I am not prepared to be a Tsar. I never wanted to become one." '
            'He was conscientious, kind to his family, and utterly unsuited to rule '
            'an empire in crisis.\n\n'
            '## Bloody Sunday and 1905\n\n'
            'On January 22, 1905, troops fired on a peaceful procession of workers '
            'petitioning the tsar for reform. Hundreds died. "Bloody Sunday" triggered '
            'the Revolution of 1905 — strikes, mutinies, and the Battleship Potemkin '
            'uprising. Nicholas issued the October Manifesto promising a Duma (parliament), '
            'which bought time but resolved nothing.\n\n'
            '## Rasputin\n\n'
            'Crown Prince Alexei suffered from hemophilia. Grigory Rasputin, a Siberian '
            'mystic, appeared to relieve the boy\'s suffering through means unexplained. '
            'The Empress Alexandra became dependent on him. His influence over court '
            'appointments scandalized Russia and undermined confidence in the dynasty.\n\n'
            '## World War I\n\n'
            'Russia entered the war in August 1914. Initial patriotic enthusiasm faded '
            'before catastrophic defeats — Tannenberg, the Masurian Lakes. By 1916, '
            'Russia had suffered perhaps five million casualties. Supply and morale '
            'collapsed. Nicholas personally took command of the armies in 1915, '
            'a decision that tied the dynasty\'s fate to the war\'s outcome.\n\n'
            '## Abdication and Execution\n\n'
            'The February Revolution erupted in Petrograd in March 1917. Bread riots '
            'became a general strike; the army refused to fire on crowds. Nicholas\'s '
            'generals advised abdication. He signed the abdication document on March 15, '
            'surrendering the throne for himself and his son.\n\n'
            'The family was moved east as the Bolsheviks consolidated power. On the night '
            'of July 16–17, 1918, Nicholas, Alexandra, their five children, and four '
            'servants were shot in the basement of the Ipatiev House in Yekaterinburg. '
            'The Romanov dynasty was over.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Seeds the Romanov Dynasty era, periods, and 18 tsars'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing records instead of skipping',
        )

    def handle(self, *args, **options):
        force = options['force']

        # Era
        era, created = Era.objects.get_or_create(slug=ERA['slug'], defaults=ERA)
        if not created and force:
            Era.objects.filter(slug=ERA['slug']).update(**{
                k: v for k, v in ERA.items() if k != 'slug'
            })
            era.refresh_from_db()
        self.stdout.write(f"{'Created' if created else 'Exists'}: Era — {era.name}")

        # Periods
        periods = {}
        for pd in PERIODS:
            data = {**pd, 'era': era}
            slug = data.pop('slug')
            period, created = Period.objects.get_or_create(
                slug=slug, defaults={**data, 'slug': slug}
            )
            if not created and force:
                Period.objects.filter(slug=slug).update(**data)
                period.refresh_from_db()
            periods[slug] = period
            self.stdout.write(f"  {'Created' if created else 'Exists'}: Period — {period.name}")

        # Tsars
        people = {}
        for tsar in TSARS:
            period_slug = tsar.pop('period_slug')
            data = {
                **tsar,
                'era': era,
                'period': periods.get(period_slug),
                'nationality': 'Russian',
                'status': 'published',
            }
            slug = data.pop('slug')
            person, created = Person.objects.get_or_create(
                slug=slug, defaults={**data, 'slug': slug}
            )
            if not created and force:
                Person.objects.filter(slug=slug).update(**{
                    k: v for k, v in data.items() if k not in ('tags',)
                })
                person.refresh_from_db()
            people[slug] = person
            self.stdout.write(
                f"  {'Created' if created else 'Exists'}: {person.name} "
                f"({person.reign_start}–{person.reign_end})"
            )

        # Succession relationships
        tsar_slugs = [t.get('slug', None) or list(people.keys())[i]
                      for i, t in enumerate(TSARS)]
        # Re-read slugs from TSARS (already popped period_slug above in loop, so reconstruct)
        ordered_slugs = [
            'michael-i', 'alexis-i', 'feodor-iii', 'ivan-v', 'peter-i',
            'catherine-i', 'peter-ii', 'anna', 'ivan-vi', 'elizabeth',
            'peter-iii', 'catherine-ii', 'paul-i', 'alexander-i', 'nicholas-i',
            'alexander-ii', 'alexander-iii', 'nicholas-ii',
        ]
        person_ct = ContentType.objects.get_for_model(Person)
        rel_count = 0
        for i in range(len(ordered_slugs) - 1):
            pred = people.get(ordered_slugs[i])
            succ = people.get(ordered_slugs[i + 1])
            if not pred or not succ:
                continue
            # predecessor → successor: "followed"
            _, created = Relationship.objects.get_or_create(
                from_entity_type=person_ct,
                from_entity_id=pred.pk,
                to_entity_type=person_ct,
                to_entity_id=succ.pk,
                relationship_type='followed',
                defaults={
                    'description': f'{succ.name} succeeded {pred.name} as ruler of Russia.',
                    'strength': 5,
                    'is_bidirectional': False,
                }
            )
            if created:
                rel_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Created {rel_count} succession relationships.'
        ))
        self.stdout.write(
            'Run: uv run python manage.py ai_seed --help  '
            'to generate richer content with Claude.'
        )
