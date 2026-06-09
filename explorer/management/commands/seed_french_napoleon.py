"""
Management command: seed_french_napoleon
Creates the French Revolution (1789-1799) and Napoleonic Era (1799-1815) with
cross-era relationships to the Romanov Dynasty (especially Alexander I).
Idempotent — safe to run multiple times.
"""
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from explorer.models import Era, Event, Period, Person, Relationship

# ── Eras ──────────────────────────────────────────────────────────────────────

ERAS = [
    {
        'name': 'French Revolution',
        'slug': 'french-revolution',
        'tagline': 'Liberty, Equality, Fraternity — and the Terror, 1789–1799',
        'summary': (
            'The French Revolution dismantled a millennium of monarchy in less than a decade, '
            'executing a king, unleashing the Reign of Terror, and transforming European '
            'politics forever. From the storming of the Bastille to Napoleon\'s coup, '
            'France convulsed through constitutional monarchy, republic, and dictatorship.'
        ),
        'body': (
            '## The Crisis of the Ancien Régime\n\n'
            'By 1789, France was bankrupt from the American Revolutionary War and crippled '
            'by aristocratic tax exemptions. Louis XVI, weak and irresolute, summoned the '
            'Estates-General for the first time since 1614. The Third Estate — representing '
            'the commoners — seized the moment and declared itself a National Assembly.\n\n'
            '## The Revolutionary Cascade\n\n'
            'The storming of the [[bastille-1789]] on July 14, 1789 transformed political '
            'crisis into revolution. The National Assembly abolished feudalism, issued the '
            '[[declaration-rights-of-man]], and began drafting a constitution. [[louis-xvi]] '
            'found himself a constitutional monarch in a world he could not comprehend.\n\n'
            '## The Terror\n\n'
            'The execution of [[louis-xvi]] in January 1793 and war against Austria and '
            'Prussia radicalized the Revolution. [[maximilien-robespierre]] and the Committee '
            'of Public Safety launched the Reign of Terror, executing some 17,000 people '
            'and imprisoning hundreds of thousands. When Robespierre himself fell on '
            '9 Thermidor (July 27, 1794), the Terror ended.\n\n'
            '## The Directory and the Rise of Napoleon\n\n'
            'The conservative Directory (1795–1799) presided over corruption and military '
            'adventure. A young Corsican general, [[napoleon-bonaparte]], made his name '
            'in Italy and Egypt before seizing power in the coup of 18 Brumaire (1799), '
            'ending the Revolution and opening the Napoleonic Era.'
        ),
        'start_year': 1789,
        'end_year': 1799,
        'color_accent': '#d4213d',
        'icon': 'bi-flag-fill',
        'order': 2,
        'status': 'published',
    },
    {
        'name': 'Napoleonic Era',
        'slug': 'napoleonic-era',
        'tagline': "Napoleon's Europe — from Consulate to Waterloo, 1799–1815",
        'summary': (
            'Napoleon Bonaparte\'s meteoric rise reshaped Europe through conquest, law, '
            'and force of personality. From consul to emperor, he built an empire '
            'stretching from Portugal to Moscow — before it unravelled in the snows '
            'of Russia and on the fields of Waterloo.'
        ),
        'body': (
            '## The Consulate\n\n'
            'Napoleon seized power in the coup of 18 Brumaire (November 9, 1799) and '
            'installed himself as First Consul. The Consulate brought stability after '
            'a decade of revolution: the Napoleonic Code (1804) systematized French law, '
            'the Concordat (1801) reconciled France with the Catholic Church, and '
            'the Banque de France stabilized the currency.\n\n'
            '## The Empire at its Zenith\n\n'
            'Crowned Emperor in December 1804 before a stunned Pope Pius VII, Napoleon '
            'dominated Europe within two years. The destruction of the Austro-Russian '
            'army at [[battle-of-austerlitz]] (December 2, 1805) confirmed French '
            'supremacy on land. Only Britain, protected by its navy after [[battle-of-trafalgar]], '
            'remained undefeated.\n\n'
            '## The Russian Catastrophe\n\n'
            'The fatal overreach came in 1812. Napoleon led 600,000 men into Russia '
            'to force [[alexander-i]] to abandon the Continental System. The Grande Armée '
            'reached Moscow only to find it burning. Alexander refused to negotiate. '
            'The retreat cost France perhaps 400,000 men. The myth of Napoleonic '
            'invincibility was broken.\n\n'
            '## The Fall\n\n'
            'A coalition of Russia, Prussia, Austria, and Britain crushed Napoleon at '
            '[[battle-of-nations-leipzig]] (October 1813). He abdicated in April 1814, '
            'returned for the [[hundred-days]] in 1815, and was destroyed at '
            '[[battle-of-waterloo]] by Wellington and Blücher. Exiled to St. Helena, '
            'he died in 1821 — a legend even in defeat.'
        ),
        'start_year': 1799,
        'end_year': 1815,
        'color_accent': '#002395',
        'icon': 'bi-award-fill',
        'order': 3,
        'status': 'published',
    },
]

# ── Periods ────────────────────────────────────────────────────────────────────

PERIODS = {
    'french-revolution': [
        {
            'slug': 'constitutional-phase',
            'name': 'Constitutional Phase',
            'start_year': 1789, 'end_year': 1792, 'order': 1, 'status': 'published',
            'summary': (
                'The National Assembly dismantled the Ancien Régime, abolished feudalism, '
                'issued the Declaration of the Rights of Man, and drafted a constitution '
                'making Louis XVI a constitutional monarch. France transformed rapidly, '
                'but war with Austria and Prussia loomed.'
            ),
        },
        {
            'slug': 'the-terror',
            'name': 'The Terror',
            'start_year': 1792, 'end_year': 1794, 'order': 2, 'status': 'published',
            'summary': (
                'War, foreign invasion, and radical politics combined to produce the most '
                'violent phase of the Revolution. The monarchy was abolished, Louis XVI '
                'was guillotined, and Robespierre\'s Committee of Public Safety executed '
                'thousands before the Thermidorian Reaction ended the bloodshed.'
            ),
        },
        {
            'slug': 'the-directory',
            'name': 'The Directory',
            'start_year': 1795, 'end_year': 1799, 'order': 3, 'status': 'published',
            'summary': (
                'The conservative Directory governed France through corruption and '
                'military expansion. Napoleon\'s Italian and Egyptian campaigns made '
                'him the republic\'s most celebrated general, positioning him for '
                'the coup that ended the Revolution.'
            ),
        },
    ],
    'napoleonic-era': [
        {
            'slug': 'consulate',
            'name': 'The Consulate',
            'start_year': 1799, 'end_year': 1804, 'order': 1, 'status': 'published',
            'summary': (
                'Napoleon consolidated power as First Consul, then Consul for Life. '
                'He reformed French law (Napoleonic Code), reconciled with the Church '
                '(Concordat), and defeated Austria at Marengo — all while slowly '
                'transforming the republic into a personal autocracy.'
            ),
        },
        {
            'slug': 'first-french-empire',
            'name': 'First French Empire',
            'start_year': 1804, 'end_year': 1812, 'order': 2, 'status': 'published',
            'summary': (
                'Napoleon at his height: crowned Emperor, victorious at Austerlitz, '
                'Jena, and Wagram. The Continental System attempted to strangle Britain '
                'economically. French law, culture, and imperial power spread across '
                'Europe — until Russia broke the spell.'
            ),
        },
        {
            'slug': 'napoleonic-fall',
            'name': 'The Fall',
            'start_year': 1812, 'end_year': 1815, 'order': 3, 'status': 'published',
            'summary': (
                'The catastrophic Russian campaign of 1812 shattered the Grande Armée. '
                'A European coalition finished the work at Leipzig (1813) and Waterloo (1815). '
                'Napoleon died in exile on St. Helena in 1821, his legend outlasting his empire.'
            ),
        },
    ],
}

# ── People ─────────────────────────────────────────────────────────────────────

PEOPLE = {
    'french-revolution': [
        {
            'name': 'Louis XVI',
            'slug': 'louis-xvi',
            'title': 'King of France and Navarre',
            'period_slug': 'constitutional-phase',
            'birth_year': 1754, 'death_year': 1793,
            'reign_start': 1774, 'reign_end': 1792,
            'nationality': 'French',
            'summary': (
                'The last absolute King of France, Louis XVI was well-meaning but '
                'indecisive, unable to grasp the scale of change sweeping his kingdom. '
                'He was guillotined on January 21, 1793, becoming a symbol of the '
                'revolution\'s radicalization and the terror of its consequences.'
            ),
            'body': (
                '## The Accidental King\n\n'
                'Louis Auguste inherited the French throne at twenty, ill-prepared for '
                'absolute rule. His passions were locksmithing and hunting, not statecraft. '
                'His marriage to the Austrian archduchess [[marie-antoinette]] was '
                'politically motivated — and produced a queen who became the revolution\'s '
                'most hated symbol.\n\n'
                '## Fiscal Crisis and Estates-General\n\n'
                'France\'s support for the American Revolution had bankrupted the treasury. '
                'Unable to tax the nobility without their consent, Louis convened the '
                'Estates-General in May 1789 — the first time since 1614. The Third '
                'Estate\'s demand for more representation ignited the Revolution.\n\n'
                '## Constitutional Monarch\n\n'
                'Louis accepted the constitutional settlement of 1791, but his heart was '
                'never in it. His attempted flight to Varennes in June 1791 — aiming to '
                'join Austrian forces — destroyed his remaining credibility. Arrested and '
                'returned to Paris, he was a prisoner king.\n\n'
                '## Trial and Execution\n\n'
                'After the storming of the Tuileries and the fall of the monarchy (August '
                '1792), Louis was tried before the National Convention. Found guilty of '
                '"conspiracy against liberty," he was guillotined at the Place de la '
                'Révolution on January 21, 1793. His composed dignity at the scaffold '
                'made him a martyr to royalists across Europe.'
            ),
        },
        {
            'name': 'Marie Antoinette',
            'slug': 'marie-antoinette',
            'title': 'Queen of France',
            'period_slug': 'constitutional-phase',
            'birth_year': 1755, 'death_year': 1793,
            'reign_start': 1774, 'reign_end': 1792,
            'nationality': 'Austrian',
            'summary': (
                'Austrian princess who became Queen of France and the revolution\'s '
                'most despised symbol. Caricatured as "Madame Deficit" for her extravagance, '
                'she was guillotined nine months after her husband, at age 37.'
            ),
            'body': (
                '## The Habsburg Bride\n\n'
                'Maria Antonia of Austria was sent to France at fourteen as a diplomatic '
                'pawn, married to the heir apparent. Renamed Marie Antoinette, she arrived '
                'at a court that was already beginning to resent Austria. Her youth, '
                'vivacity, and spending became scandal fodder for an increasingly '
                'hostile press.\n\n'
                '## Symbol of Excess\n\n'
                'The Affair of the Diamond Necklace (1785) — in which she was falsely '
                'implicated in a fraud — destroyed her remaining public sympathy. '
                'Pamphlets portrayed her as "Madame Deficit," draining France\'s treasury '
                'for Austrian interests. Her actual spending, while lavish, was minor '
                'compared to the deficits created by war and aristocratic privilege.\n\n'
                '## Captivity and Trial\n\n'
                'After Varennes and the fall of the monarchy, Marie Antoinette was '
                'imprisoned in the Temple and later the Conciergerie. Her trial before '
                'the Revolutionary Tribunal in October 1793 included fabricated charges '
                'of incest. She was guillotined on October 16, 1793. Her dignified '
                'bearing in captivity gradually transformed her public image from '
                'villain to martyr.'
            ),
        },
        {
            'name': 'Maximilien Robespierre',
            'slug': 'maximilien-robespierre',
            'title': 'Member of the Committee of Public Safety',
            'period_slug': 'the-terror',
            'birth_year': 1758, 'death_year': 1794,
            'nationality': 'French',
            'summary': (
                'The "Incorruptible" — a lawyer from Arras who became the revolution\'s '
                'most powerful figure and the architect of the Reign of Terror. '
                'Robespierre\'s belief that virtue required violence consumed tens of '
                'thousands of lives before the Thermidorian Reaction guillotined him '
                'on July 28, 1794.'
            ),
            'body': (
                '## The Incorruptible\n\n'
                'Maximilien Robespierre arrived at the Estates-General in 1789 as a '
                'provincial lawyer, a disciple of Rousseau, and an idealist. He earned '
                'his nickname "the Incorruptible" for refusing bribes and living simply '
                'while preaching civic virtue. He was among the first to advocate for '
                'universal male suffrage and the abolition of slavery.\n\n'
                '## Rise to Power\n\n'
                'As the Revolution radicalized under the pressure of war and counter-'
                'revolution, Robespierre\'s uncompromising Jacobin republicanism became '
                'an asset. By mid-1793, he dominated the Committee of Public Safety — '
                'effectively the revolutionary government.\n\n'
                '## The Terror\n\n'
                'Robespierre justified mass executions as necessary to preserve the '
                'Revolution against its enemies. "Terror is nothing other than justice, '
                'prompt, severe, inflexible," he declared. Under the Law of 22 Prairial '
                '(June 1794), defendants lost the right to counsel or to call witnesses. '
                'The guillotine worked without pause.\n\n'
                '## The Fall\n\n'
                'By late July 1794, even Robespierre\'s allies feared they were next. '
                'On 9 Thermidor (July 27, 1794), the Convention turned on him. Arrested '
                'and guillotined the following day, he died as he had lived — convinced '
                'of his own righteousness. His death ended the Terror but left the '
                'question of how virtue and liberty could coexist permanently unresolved.'
            ),
        },
        {
            'name': 'Georges Danton',
            'slug': 'georges-danton',
            'title': 'Minister of Justice; President of the Committee of Public Safety',
            'period_slug': 'the-terror',
            'birth_year': 1759, 'death_year': 1794,
            'nationality': 'French',
            'summary': (
                'The thunderous orator who rallied France against foreign invasion in 1792 '
                '— "De l\'audace, encore de l\'audace, toujours de l\'audace!" His moderation '
                'in the Terror made him dangerous; Robespierre sent him to the guillotine '
                'in April 1794.'
            ),
            'body': (
                '## The Voice of Revolution\n\n'
                'Georges Danton was the Revolution\'s great improviser — a large, '
                'physically powerful man with a voice that could fill a square and a '
                'talent for sensing the popular mood. He was instrumental in organizing '
                'the defense of France against foreign invasion in 1792, and his call '
                '"Boldness, more boldness, always boldness!" became a revolutionary '
                'rallying cry.\n\n'
                '## Organizer of Victory\n\n'
                'As Minister of Justice and then Committee of Public Safety president, '
                'Danton helped organize the *levée en masse* (mass conscription) that '
                'built the army that would eventually conquer Europe under Napoleon. '
                'He was also involved in establishing the Revolutionary Tribunal — '
                'a sword that would eventually fall on him.\n\n'
                '## Indulgent and Doomed\n\n'
                'By 1793, Danton had grown tired of the Terror and began calling for '
                'clemency — becoming leader of the "Indulgents." Robespierre saw this '
                'as weakness or treason. In April 1794, Danton and his allies were '
                'arrested, tried in a show proceeding, and guillotined. His last words '
                'were said to be: "Above all, don\'t forget to show my head to the people '
                '— it\'s worth seeing."'
            ),
        },
        {
            'name': 'Marquis de Lafayette',
            'slug': 'marquis-de-lafayette',
            'title': 'Major-General; Commander of the National Guard',
            'period_slug': 'constitutional-phase',
            'birth_year': 1757, 'death_year': 1834,
            'nationality': 'French',
            'summary': (
                'Hero of both the American and French revolutions, Lafayette commanded '
                'the National Guard and drafted the Declaration of the Rights of Man. '
                'His commitment to constitutional monarchy placed him between extremes, '
                'and he fled France in 1792 as the revolution passed him by.'
            ),
            'body': (
                '## The American Volunteer\n\n'
                'At nineteen, the Marquis de Lafayette sailed to America to fight for '
                'independence, becoming Washington\'s trusted aide. He returned to France '
                'in 1782 a hero, bringing Enlightenment ideals forged in combat.\n\n'
                '## Architect of 1789\n\n'
                'Lafayette drafted the Declaration of the Rights of Man (with Jefferson\'s '
                'advice) and commanded the National Guard in Paris. He tried to steer '
                'France toward a constitutional monarchy modeled on Britain — navigating '
                'between Louis XVI\'s conservatism and the Jacobins\' radicalism.\n\n'
                '## Between Two Revolutions\n\n'
                'When the monarchy fell in August 1792, Lafayette\'s constitutional '
                'position became untenable. Fleeing toward neutral territory, he was '
                'captured by Austrian forces and imprisoned for five years. He survived '
                'to see Napoleon, the Restoration, and the Revolution of 1830 — dying '
                'in 1834 as the last living major figure of 1789.'
            ),
        },
    ],
    'napoleonic-era': [
        {
            'name': 'Napoleon Bonaparte',
            'slug': 'napoleon-bonaparte',
            'title': 'Emperor of the French',
            'period_slug': 'first-french-empire',
            'birth_year': 1769, 'death_year': 1821,
            'reign_start': 1799, 'reign_end': 1815,
            'nationality': 'French (born Corsican)',
            'summary': (
                'Soldier, consul, emperor, and exile — Napoleon Bonaparte\'s career '
                'compressed a century of European history into sixteen years. He reformed '
                'French law, conquered most of Europe, and was ultimately destroyed by '
                'the Russian winter and the coalition it inspired. His legend outlasted '
                'his empire by two centuries.'
            ),
            'body': (
                '## The Corsican Outsider\n\n'
                'Born in Ajaccio, Corsica, just one year after France acquired the island '
                'from Genoa, Napoleon attended French military schools on scholarship. '
                'A second lieutenant at sixteen, he threw himself into the Revolution '
                'as an opportunity. His artillery command at the siege of Toulon (1793) '
                'caught the Committee of Public Safety\'s attention.\n\n'
                '## Italian Campaigns and Egyptian Adventure\n\n'
                'Given command of the Army of Italy in 1796, Napoleon transformed a '
                'starving rabble into a conquering force in weeks. In a year, he had '
                'driven Austria from northern Italy and dictated peace terms. The '
                'Egyptian campaign (1798–99) was militarily mixed but launched Napoleon\'s '
                'mythology — he returned to France at just the right moment.\n\n'
                '## The Coup and Consolidation\n\n'
                'The coup of 18 Brumaire (November 9, 1799) made Napoleon First Consul. '
                'He stabilized France with breathtaking speed: the Napoleonic Code (1804), '
                'the Concordat with the Church, the Bank of France, the *lycée* system. '
                'The plebiscite making him Emperor was more ratification than election.\n\n'
                '## The Great Years\n\n'
                'Austerlitz (1805), Jena (1806), Wagram (1809) — Napoleon\'s strategic '
                'genius seemed unlimited. He placed his brothers on European thrones, '
                'codified law across a continent, and inspired a generation of soldiers '
                'who followed him anywhere. Only Britain, behind its naval shield, '
                'remained beyond reach.\n\n'
                '## Russia and the Fall\n\n'
                'The [[invasion-of-russia-1812]] was the hinge of history. Six hundred '
                'thousand men entered; fewer than one hundred thousand returned. [[alexander-i]] '
                'refused to make peace, and Russia\'s vast spaces swallowed the Grande Armée. '
                'The coalition that followed — Russia, Prussia, Austria, Britain — '
                'destroyed Napoleon at [[battle-of-nations-leipzig]] and forced his '
                'first abdication (April 1814). The [[hundred-days]] ended at '
                '[[battle-of-waterloo]] on June 18, 1815. Napoleon died on St. Helena '
                'on May 5, 1821.'
            ),
        },
        {
            'name': 'Joséphine de Beauharnais',
            'slug': 'josephine-de-beauharnais',
            'title': 'Empress of the French',
            'period_slug': 'first-french-empire',
            'birth_year': 1763, 'death_year': 1814,
            'reign_start': 1804, 'reign_end': 1809,
            'nationality': 'French (born Martinican)',
            'summary': (
                'Born in Martinique, widowed by the Terror, Joséphine became Napoleon\'s '
                'first wife and Empress of the French. Their famously passionate and '
                'turbulent marriage ended in divorce in 1809 when Napoleon needed a '
                'dynastic heir she had failed to provide.'
            ),
            'body': (
                '## From Martinique to Paris\n\n'
                'Marie Josèphe Rose Tascher de La Pagerie was born to a minor aristocratic '
                'family in Martinique. Sent to France at sixteen to marry Viscount de '
                'Beauharnais, she survived the Terror (her husband was guillotined) '
                'and emerged as one of Paris\'s most fashionable women.\n\n'
                '## Empress\n\n'
                'Napoleon met Joséphine in 1795 and was immediately obsessed. Their '
                'marriage in 1796 preceded his Italian triumphs. She was crowned Empress '
                'at Notre-Dame in December 1804. Her taste shaped the Empire style that '
                'defined an era of European decoration and fashion.\n\n'
                '## Divorce\n\n'
                'Unable to produce an heir after thirteen years of marriage, Joséphine '
                'was divorced in December 1809. Napoleon\'s letter announcing his decision '
                'was one of his most personal: "My feeling for you has not changed, but '
                'politics and France\'s need of an heir have prevailed." She retired to '
                'Malmaison, where she died in May 1814, shortly after Napoleon\'s abdication.'
            ),
        },
        {
            'name': 'Marshal Michel Ney',
            'slug': 'marshal-michel-ney',
            'title': 'Marshal of France; Prince of Moscow',
            'period_slug': 'first-french-empire',
            'birth_year': 1769, 'death_year': 1815,
            'nationality': 'French',
            'summary': (
                '"The Bravest of the Brave" — Napoleon\'s finest combat commander, '
                'who personally led the rearguard during the catastrophic retreat from '
                'Moscow. He rejoined Napoleon during the Hundred Days and was executed '
                'by the Bourbon government as a traitor on December 7, 1815.'
            ),
            'body': (
                '## Soldier\'s Soldier\n\n'
                'Michel Ney rose from the son of a barrel-maker to become one of the '
                'eighteen Marshals of the Empire — the greatest military rank France '
                'had ever created. Napoleon called him "the bravest of the brave" '
                'after watching him fight at Friedland (1807).\n\n'
                '## The Retreat from Moscow\n\n'
                'Ney\'s finest hour came in catastrophe. Commanding the rearguard during '
                'the retreat from Moscow, he held off Russian pursuit again and again '
                'with troops that barely existed. He was among the last French soldiers '
                'to cross the Niemen river back into Poland, having lost virtually '
                'his entire corps but preserving the remnant of the Grande Armée.\n\n'
                '## The Hundred Days and the Firing Squad\n\n'
                'When Napoleon returned from Elba in 1815, Ney — sent to arrest him — '
                'instead embraced him and rejoined the cause. After Waterloo, the Bourbon '
                'government tried Ney for treason. He was executed by firing squad '
                'on December 7, 1815. He reportedly commanded his own execution, '
                'refusing the blindfold: "Soldiers, when I give the command to fire, '
                'fire straight at my heart."'
            ),
        },
        {
            'name': 'Duke of Wellington',
            'slug': 'duke-of-wellington',
            'title': 'Field Marshal; Duke of Wellington',
            'period_slug': 'napoleonic-fall',
            'birth_year': 1769, 'death_year': 1852,
            'nationality': 'British (Irish-born)',
            'summary': (
                'Arthur Wellesley defeated Napoleon at Waterloo on June 18, 1815 — '
                'the battle that ended the Napoleonic Era. A meticulous defensive '
                'strategist, Wellington famously described the battle as "the nearest '
                'run thing you ever saw in your life." He later served as British '
                'Prime Minister.'
            ),
            'body': (
                '## The Sepoy General\n\n'
                'Arthur Wellesley made his military reputation in India, defeating Tipu '
                'Sultan and pacifying the Maratha Confederacy before most Europeans had '
                'heard of Napoleon. Knighted in 1804, he arrived in Portugal in 1808 '
                'as an unknown quantity.\n\n'
                '## The Peninsular Campaign\n\n'
                'For six years, Wellington fought the Peninsular War in Spain and Portugal '
                '— tying down over 300,000 French troops that Napoleon desperately needed '
                'elsewhere. His victory at Salamanca (1812) and entry into Madrid was '
                'coordinated, in its effects, with the Russian catastrophe of the same year.\n\n'
                '## Waterloo\n\n'
                'Commanding the Anglo-Dutch army against Napoleon\'s final bid, Wellington '
                'held the ridge of Mont-Saint-Jean throughout June 18, 1815 — sustaining '
                'horrific casualties but not breaking. When Blücher\'s Prussians arrived '
                'in the late afternoon, the combined pressure destroyed the French army. '
                'Wellington called it "the nearest run thing you ever saw in your life." '
                'He spent the night weeping for his fallen officers.'
            ),
        },
        {
            'name': 'Charles-Maurice de Talleyrand',
            'slug': 'talleyrand',
            'title': 'Foreign Minister of France; Prince of Benevento',
            'period_slug': 'consulate',
            'birth_year': 1754, 'death_year': 1838,
            'nationality': 'French',
            'summary': (
                'The supreme survivor of European politics: bishop under the Ancien Régime, '
                'revolutionary diplomat, Napoleon\'s foreign minister, and architect of the '
                'post-Napoleonic settlement at the Congress of Vienna. He served every '
                'French government from Louis XVI to Louis-Philippe.'
            ),
            'body': (
                '## The Eternal Diplomat\n\n'
                'Charles-Maurice de Talleyrand-Périgord was born lame, steered into the '
                'Church against his will, and emerged as France\'s greatest diplomat. '
                'Bishop of Autun in 1789, he proposed the nationalization of Church '
                'property to solve the fiscal crisis — an act that got him '
                'excommunicated but endeared him to the Revolution.\n\n'
                '## Napoleon\'s Foreign Minister\n\n'
                'Talleyrand served Napoleon as Foreign Minister (1799–1807), negotiating '
                'the Concordat, the Treaty of Amiens, and the Peace of Pressburg. '
                'But he grew increasingly alarmed by Napoleon\'s expansionism, eventually '
                'secretly passing information to the coalition powers. Napoleon called '
                'him "a turd in silk stockings."\n\n'
                '## The Congress of Vienna\n\n'
                'At the [[congress-of-vienna]] (1814–15), Talleyrand performed his '
                'greatest feat: representing defeated France as an equal power and '
                'preventing the vindictive dismemberment of the country. His principle '
                'of "legitimacy" — restoring lawful sovereigns — gave France a '
                'diplomatic framework to re-enter European politics.'
            ),
        },
    ],
}

# ── Events ─────────────────────────────────────────────────────────────────────

EVENTS = {
    'french-revolution': [
        {
            'name': 'Storming of the Bastille',
            'slug': 'bastille-1789',
            'event_type': 'revolution',
            'period_slug': 'constitutional-phase',
            'year': 1789, 'location': 'Paris, France',
            'summary': (
                'On July 14, 1789, Parisian crowds stormed the Bastille fortress-prison, '
                'freeing its seven prisoners and seizing its gunpowder. The symbolic '
                'act of defiance against royal tyranny became the Revolution\'s '
                'founding myth — and France\'s national day.'
            ),
            'body': (
                '## The Day the Revolution Began\n\n'
                'The Bastille was an obsolete medieval fortress housing only seven '
                'prisoners when the mob arrived. But as a symbol of royal despotism, '
                'it was everything. Rumors that Louis XVI was massing troops to dissolve '
                'the National Assembly triggered panic in Paris. Armed citizens '
                'and mutinous soldiers attacked the fortress on the morning of July 14.\n\n'
                '## The Siege\n\n'
                'After a chaotic siege in which 98 attackers were killed, the Bastille\'s '
                'governor, Bernard-René de Launay, surrendered. He was lynched by the '
                'crowd moments after the gates opened. His head was paraded through '
                'Paris on a pike.\n\n'
                '## Legacy\n\n'
                'When Louis XVI was told of the storming, he reportedly said: "Is it '
                'a revolt?" His courtier replied: "No, Sire, it is a revolution." '
                'July 14 became the Fête Nationale — Bastille Day — the symbol of '
                'popular sovereignty against tyranny.'
            ),
        },
        {
            'name': 'Declaration of the Rights of Man',
            'slug': 'declaration-rights-of-man',
            'event_type': 'political',
            'period_slug': 'constitutional-phase',
            'year': 1789, 'location': 'Versailles, France',
            'summary': (
                'Adopted by the National Assembly on August 26, 1789, the Declaration '
                'of the Rights of Man and of the Citizen proclaimed liberty, equality, '
                'popular sovereignty, and the rule of law. Drafted partly with Thomas '
                'Jefferson\'s advice, it became the founding document of modern human rights.'
            ),
            'body': (
                '## Enlightenment into Law\n\n'
                'The Declaration translated Enlightenment philosophy — Rousseau\'s '
                'social contract, Locke\'s natural rights, Montesquieu\'s separation '
                'of powers — into seventeen articles with the force of constitutional law. '
                'It proclaimed that "the principle of sovereignty resides essentially '
                'in the Nation" and that law must be "the expression of the general will."\n\n'
                '## Lafayette and Jefferson\n\n'
                '[[marquis-de-lafayette]] drafted the Declaration with informal input '
                'from Thomas Jefferson, then the American ambassador in Paris. Jefferson '
                'wrote that he suggested "moderate" changes — a reminder of how closely '
                'the American and French revolutions shaped each other.\n\n'
                '## Lasting Impact\n\n'
                'The Declaration influenced the United Nations\' Universal Declaration '
                'of Human Rights (1948) and remains a cornerstone of French constitutional '
                'law. Its promise that all men are "born and remain free and equal in '
                'rights" echoed — and was contested — across two centuries of revolution, '
                'colonialism, and liberation.'
            ),
        },
        {
            'name': 'Execution of Louis XVI',
            'slug': 'execution-of-louis-xvi',
            'event_type': 'political',
            'period_slug': 'the-terror',
            'year': 1793, 'location': 'Paris, France',
            'summary': (
                'On January 21, 1793, King Louis XVI was guillotined at the Place de '
                'la Révolution before a vast crowd. The regicide shocked monarchies '
                'across Europe, triggered war with Britain, and marked the Revolution\'s '
                'decisive break with the old order.'
            ),
            'body': (
                '## The Trial\n\n'
                'The National Convention tried Louis XVI in December 1792 on charges '
                'of "conspiracy against liberty and crimes against the state." Evidence '
                'included secret correspondence with foreign courts found in the '
                'Tuileries iron safe. He was found guilty by near-unanimous vote; '
                'the vote for execution passed 361 to 360.\n\n'
                '## The Execution\n\n'
                'Louis XVI was driven to the scaffold in a carriage, through streets '
                'lined with armed guards. He attempted to address the crowd: "I die '
                'innocent of all the crimes laid to my charge." The drum roll drowned '
                'him out. The guillotine blade fell at 10:22 am.\n\n'
                '## European Reaction\n\n'
                'The execution triggered immediate declarations of war from Britain, '
                'Holland, and Spain — joining Austria and Prussia already at war with '
                'France. The Coalition that formed would fight France, with brief '
                'interruptions, for the next twenty-two years. For [[alexander-i]] '
                'of Russia, the regicide became a lifelong obsession — one reason he '
                'refused to treat with [[napoleon-bonaparte]] after 1812.'
            ),
        },
        {
            'name': 'Reign of Terror',
            'slug': 'reign-of-terror',
            'event_type': 'revolution',
            'period_slug': 'the-terror',
            'year': 1793, 'end_year': 1794,
            'location': 'France',
            'summary': (
                'Under [[maximilien-robespierre]] and the Committee of Public Safety, '
                'France executed approximately 17,000 people and imprisoned 300,000 '
                'more between September 1793 and July 1794. The Terror was justified '
                'as defense of the Revolution against internal enemies — until it '
                'consumed its own architects.'
            ),
            'body': (
                '## Origins\n\n'
                'The Terror grew from genuine crisis: Austria and Prussia had invaded, '
                'the Vendée region was in counter-revolutionary revolt, and the '
                'Revolution\'s enemies seemed everywhere. The Law of Suspects (September '
                '1793) defined enemies so broadly that almost anyone could be arrested.\n\n'
                '## The Machinery\n\n'
                'The Revolutionary Tribunal worked without appeal. Defendants were '
                'denied counsel; conviction required only the jury\'s "moral certainty." '
                'The guillotine worked so efficiently in Paris that ox carts were needed '
                'to carry bodies from the Place de la Révolution. In Lyon, Nantes, '
                'and other rebel cities, mass drownings and shootings supplemented '
                'the guillotine.\n\n'
                '## Thermidor\n\n'
                'The Terror\'s end came not from popular revolt but from fear within '
                'the Committee itself. In July 1794, Robespierre had begun denouncing '
                'unnamed colleagues as traitors. The Convention struck first: Robespierre '
                'was arrested on 9 Thermidor (July 27, 1794) and guillotined the '
                'following day. The Terror\'s end came as abruptly as a blade.'
            ),
        },
        {
            'name': 'Coup of 18 Brumaire',
            'slug': 'coup-18-brumaire',
            'event_type': 'political',
            'period_slug': 'the-directory',
            'year': 1799, 'location': 'Saint-Cloud, France',
            'summary': (
                'On November 9, 1799 (18 Brumaire Year VIII), Napoleon Bonaparte '
                'overthrew the Directory with military force, ending the French Revolution '
                'and inaugurating the Consulate. Napoleon became First Consul — '
                'effectively dictator — within days.'
            ),
            'body': (
                '## The Directory\'s Weakness\n\n'
                'By 1799, the Directory was discredited — corrupt, incompetent, and '
                'facing military reverses in Italy and the Rhine. Several directors '
                'approached Napoleon, freshly returned from Egypt, to lead a coup. '
                'Sieyès, the constitutional theorist, provided the pretext: a '
                '"conspiracy of Jacobins" requiring emergency measures.\n\n'
                '## The Coup\n\n'
                'On 18 Brumaire, Napoleon addressed the Council of Ancients at '
                'Saint-Cloud. It went badly — he was jeered, jostled, and nearly '
                'physically ejected. His brother Lucien, president of the Council '
                'of Five Hundred, intervened, telling grenadiers that daggers were '
                'being drawn on Napoleon. The deputies scattered. The coup succeeded.\n\n'
                '## Legacy\n\n'
                'Napoleon later claimed he had saved the Republic. In reality, he had '
                'buried it. Within five years he would be Emperor. Within ten, he '
                'would invade Russia. The coup of 18 Brumaire is history\'s most '
                'consequential anticlimactic moment.'
            ),
        },
    ],
    'napoleonic-era': [
        {
            'name': 'Napoleon Crowned Emperor',
            'slug': 'napoleon-crowned-emperor',
            'event_type': 'political',
            'period_slug': 'first-french-empire',
            'year': 1804, 'location': 'Notre-Dame Cathedral, Paris',
            'summary': (
                'On December 2, 1804, Napoleon crowned himself Emperor of the French '
                'in Notre-Dame Cathedral, in the presence of Pope Pius VII. By placing '
                'the crown on his own head, he signaled that his power derived not from '
                'God or Church but from himself — and from the French people.'
            ),
            'body': (
                '## The Coronation\n\n'
                'Pope Pius VII had travelled to Paris — an extraordinary concession — '
                'hoping to reassert Church influence. Napoleon had other plans. When '
                'the moment came to crown himself Emperor, he took the crown from '
                'the pope\'s hands and placed it on his own head. He then crowned '
                'Joséphine Empress.\n\n'
                '## Meaning\n\n'
                'The gesture was deliberate and theatrical. Napoleon was Caesar, not '
                'Charlemagne — his authority derived from conquest and popular will, '
                'not divine right. David\'s enormous painting of the coronation '
                '(commissioned by Napoleon) shows the pope in the background, '
                'essentially a spectator.\n\n'
                '## Reaction\n\n'
                'In Vienna, Beethoven erased Napoleon\'s name from the dedication of '
                'his Third Symphony ("Eroica"), furious that the republican hero had '
                'become a monarch. In Russia, [[alexander-i]] noted the development '
                'with quiet alarm — a year before Austerlitz.'
            ),
        },
        {
            'name': 'Battle of Trafalgar',
            'slug': 'battle-of-trafalgar',
            'event_type': 'battle',
            'period_slug': 'first-french-empire',
            'year': 1805, 'location': 'Cape Trafalgar, Spain',
            'summary': (
                'On October 21, 1805, Admiral Horatio Nelson destroyed the combined '
                'French and Spanish fleet off Cape Trafalgar, ensuring British naval '
                'supremacy for the next century. Nelson was killed in the battle. '
                'Napoleon would never successfully threaten Britain by sea again.'
            ),
            'body': (
                '## Context\n\n'
                'Napoleon had assembled the Grande Armée at Boulogne for a planned '
                'invasion of England. The plan required the French fleet to control '
                'the Channel even briefly. Admiral Villeneuve\'s combined Franco-Spanish '
                'fleet sailed from Cadiz to draw the British away.\n\n'
                '## The Battle\n\n'
                'Nelson approached in two columns perpendicular to the enemy line — '
                'a radical tactic that cut through the French formation. Fighting was '
                'at point-blank range. Nelson, identifiable on his quarterdeck, was '
                'shot by a French sniper and died four hours later as the battle\'s '
                'outcome became clear. Twenty-two enemy ships were captured or destroyed; '
                'no British ships were lost.\n\n'
                '## Consequences\n\n'
                'Trafalgar confirmed British naval invincibility. Napoleon pivoted to '
                'economic warfare — the Continental Blockade. He would never again '
                'seriously contemplate invading England. Two months later, he destroyed '
                'the Russian and Austrian armies at [[battle-of-austerlitz]].'
            ),
        },
        {
            'name': 'Battle of Austerlitz',
            'slug': 'battle-of-austerlitz',
            'event_type': 'battle',
            'period_slug': 'first-french-empire',
            'year': 1805, 'location': 'Austerlitz, Moravia (Czech Republic)',
            'summary': (
                'On December 2, 1805 — the first anniversary of his coronation — '
                'Napoleon defeated the combined armies of Russia and Austria in what '
                'many consider his tactical masterpiece. [[alexander-i]] of Russia '
                'was present and retreated in humiliation. The battle shattered '
                'the Third Coalition.'
            ),
            'body': (
                '## The Setup\n\n'
                'Napoleon deliberately feigned weakness on his right flank, '
                'inviting the Austro-Russian commanders to attack it. Emperor '
                '[[alexander-i]] and Austrian General Kutuzov (who opposed the attack) '
                'committed their best troops to the assault, weakening their center.\n\n'
                '## The Battle\n\n'
                'Napoleon\'s assault on the weakened center — the Pratzen Heights — '
                'split the allied army in two. French forces then rolled up each half. '
                'The allies lost 36,000 men to France\'s 9,000. The frozen ponds of '
                'Satschan became famous: retreating Russians fell through the ice '
                'as French artillery bombarded them.\n\n'
                '## Alexander\'s Humiliation\n\n'
                '[[alexander-i]] wept on the field. He later wrote that Austerlitz was '
                '"the most painful memory of my life." The defeat — in front of the '
                'young tsar who had led his army into battle personally — made the '
                'eventual Russian revenge of 1812 a matter of personal honor. '
                'The Peace of Pressburg stripped Austria of its Italian and German territories.'
            ),
        },
        {
            'name': 'Invasion of Russia 1812',
            'slug': 'invasion-of-russia-1812',
            'event_type': 'battle',
            'period_slug': 'napoleonic-fall',
            'year': 1812, 'end_year': 1812,
            'location': 'Russia',
            'summary': (
                'Napoleon\'s Grande Armée of 600,000 men crossed into Russia on June '
                '24, 1812. Five months later, fewer than 100,000 returned. '
                '[[alexander-i]]\'s refusal to negotiate, the burning of Moscow, and '
                'the catastrophic winter retreat broke the Napoleonic Empire.'
            ),
            'body': (
                '## Why Russia?\n\n'
                '[[alexander-i]] had abandoned Napoleon\'s Continental System — the '
                'economic blockade of Britain — in late 1810, allowing neutral ships '
                'to trade with Russia. This, for Napoleon, was intolerable. He '
                'assembled the largest army in European history: 600,000 soldiers '
                'from France and a dozen subject nations.\n\n'
                '## The Advance\n\n'
                'The Russian armies retreated rather than give battle. Napoleon, '
                'expecting a decisive engagement that would force terms, pursued deeper '
                'into Russia. The Battle of [[battle-of-borodino]] (September 7, 1812) '
                'was the bloodiest single day of the Napoleonic Wars — 70,000 casualties '
                'combined — but no decision was reached. Russia kept its army intact '
                'and continued retreating.\n\n'
                '## Moscow\n\n'
                'Napoleon entered Moscow on September 14, 1812. The city burned — '
                'Russian saboteurs, not French soldiers, set the fires. '
                'Alexander refused to negotiate. Napoleon waited five weeks, '
                'then began the retreat on October 19.\n\n'
                '## The Retreat\n\n'
                'The retreat became a catastrophe. Cossack raids, guerrilla attacks, '
                'and temperatures of −30°C destroyed units faster than combat. '
                '[[marshal-michel-ney]] commanded the rearguard. Napoleon abandoned '
                'his army in December and raced to Paris to forestall a coup. '
                'The campaign cost France 400,000 dead — and destroyed the myth '
                'of Napoleonic invincibility.'
            ),
        },
        {
            'name': 'Battle of Borodino',
            'slug': 'battle-of-borodino',
            'event_type': 'battle',
            'period_slug': 'napoleonic-fall',
            'year': 1812, 'location': 'Borodino, Russia',
            'summary': (
                'The bloodiest day of the Napoleonic Wars: 70,000 casualties as Napoleon\'s '
                'Grande Armée fought the Russian army at Borodino on September 7, 1812. '
                'Napoleon held the field but failed to destroy the Russian army, which '
                'retreated intact — ensuring the eventual French catastrophe.'
            ),
            'body': (
                '## The Battlefield\n\n'
                'Russian General Kutuzov selected a position near Borodino village, '
                'seventy miles west of Moscow, and constructed a series of redoubts. '
                'He needed a battle to satisfy public demand for defense of Moscow, '
                'even if he did not expect to win it.\n\n'
                '## The Fighting\n\n'
                'For twelve hours, Napoleon launched frontal assaults against the Russian '
                'positions. The Raevsky Redoubt changed hands three times. Napoleon '
                'withheld his Imperial Guard — the decisive reserve — and never committed '
                'it, fearing he was too far from France to risk everything.\n\n'
                '## The Aftermath\n\n'
                'Napoleon held the field; Kutuzov retreated. But Russia\'s main army '
                'survived. Kutuzov abandoned Moscow without another fight. '
                'The decision haunted Napoleon: a complete victory at Borodino might '
                'have forced [[alexander-i]] to negotiate.'
            ),
        },
        {
            'name': 'Battle of Nations (Leipzig)',
            'slug': 'battle-of-nations-leipzig',
            'event_type': 'battle',
            'period_slug': 'napoleonic-fall',
            'year': 1813, 'location': 'Leipzig, Germany',
            'summary': (
                'The largest battle in European history before World War I: 600,000 '
                'soldiers from France, Russia, Prussia, Austria, and Sweden fought '
                'at Leipzig over three days (October 16–19, 1813). Napoleon was '
                'decisively defeated, retreating across the Rhine with a shattered army.'
            ),
            'body': (
                '## The Coalition\n\n'
                'After 1812, [[alexander-i]] of Russia became the driving force behind '
                'the Sixth Coalition. He convinced Prussia and Austria to commit their '
                'armies for a final campaign. The assembled coalition force of over '
                '300,000 men converged on Leipzig from multiple directions.\n\n'
                '## Three Days of Battle\n\n'
                'Napoleon fought brilliantly on October 16 but was outnumbered '
                'two-to-one overall. On October 18, the allied ring tightened. '
                'Saxon troops defected mid-battle. On October 19, Napoleon ordered '
                'a retreat through the city. The bridge over the Elster was blown '
                'prematurely, trapping perhaps 30,000 French soldiers in the city. '
                '[[marshal-michel-ney]] managed to escape.\n\n'
                '## The Significance\n\n'
                'Leipzig ended the Continental System and destroyed French hegemony '
                'in Germany. Napoleon retreated to France. The coalition invaded '
                'in early 1814, and Napoleon abdicated in April — for the first time.'
            ),
        },
        {
            'name': 'Hundred Days',
            'slug': 'hundred-days',
            'event_type': 'political',
            'period_slug': 'napoleonic-fall',
            'year': 1815, 'end_year': 1815,
            'location': 'France',
            'summary': (
                'Napoleon escaped from Elba on February 26, 1815 and ruled France for '
                '111 days before his defeat at Waterloo. His return demonstrated both '
                'the enduring loyalty of the French army and the implacable opposition '
                'of the European powers.'
            ),
            'body': (
                '## The Return\n\n'
                'Napoleon slipped past the island\'s garrison with 700 men, landed '
                'in the south of France, and marched north. Soldiers sent to arrest '
                'him joined him instead. Marshal Ney — who had promised Louis XVIII '
                'to bring Napoleon back "in an iron cage" — embraced him and '
                'brought his army corps over.\n\n'
                '## The "Additional Act"\n\n'
                'Napoleon, chastened by experience, presented himself as a liberal '
                'constitutional monarch. He added democratic provisions to the '
                'constitution — the "Additional Act" — but few believed the '
                'transformation was genuine.\n\n'
                '## Waterloo and the End\n\n'
                'The European powers declared Napoleon an outlaw and mobilized. '
                'He struck first, invading Belgium to defeat Wellington and Blücher '
                'before they could combine. He defeated Blücher at Ligny (June 16) '
                'but failed to follow up. At [[battle-of-waterloo]] (June 18), '
                'Wellington held until the Prussians arrived. Napoleon was '
                'exiled to St. Helena, where he died in 1821.'
            ),
        },
        {
            'name': 'Battle of Waterloo',
            'slug': 'battle-of-waterloo',
            'event_type': 'battle',
            'period_slug': 'napoleonic-fall',
            'year': 1815, 'location': 'Waterloo, Belgium',
            'summary': (
                'On June 18, 1815, [[duke-of-wellington]] and Prussian Field Marshal '
                'Blücher defeated [[napoleon-bonaparte]] at Waterloo, ending the '
                'Hundred Days and the Napoleonic Era. "Waterloo" became a byword '
                'for decisive, catastrophic defeat.'
            ),
            'body': (
                '## The Day\n\n'
                'Wellington positioned his Anglo-Dutch army on the ridge of Mont-'
                'Saint-Jean, anchored by the fortified farmhouses of Hougoumont and '
                'La Haye Sainte. Napoleon attacked repeatedly throughout the day — '
                'infantry columns, the great cavalry charges of Ney, finally the '
                'Imperial Guard itself.\n\n'
                '## The Prussians Arrive\n\n'
                'As the Imperial Guard\'s assault was repulsed in the late afternoon, '
                'Blücher\'s Prussians arrived on Napoleon\'s eastern flank. The '
                'simultaneous Allied advance and Prussian pressure caused a '
                'collapse. "La Garde recule!" — the Guard falls back — '
                'triggered a rout that became a massacre.\n\n'
                '## Aftermath\n\n'
                'Napoleon abdicated four days later. Exiled to the remote South '
                'Atlantic island of St. Helena, he spent his remaining six years '
                'dictating his memoirs and shaping his legend. Wellington\'s verdict: '
                '"It has been a damned nice thing — the nearest run thing you ever saw."'
            ),
        },
        {
            'name': 'Congress of Vienna',
            'slug': 'congress-of-vienna',
            'event_type': 'political',
            'period_slug': 'napoleonic-fall',
            'year': 1814, 'end_year': 1815,
            'location': 'Vienna, Austria',
            'summary': (
                'The Congress of Vienna (September 1814 – June 1815) reshaped Europe '
                'after Napoleon. [[alexander-i]] of Russia was its dominant figure, '
                'pressing for constitutional government in Poland and a Holy Alliance '
                'of Christian monarchs. [[talleyrand]] famously represented defeated '
                'France as an equal power.'
            ),
            'body': (
                '## The Congress\n\n'
                'The plenipotentiaries of Europe — representing virtually every '
                'state from Portugal to Russia — assembled in Vienna for nine months '
                'of negotiation, punctuated by balls and banquets. The Austrian '
                'Foreign Minister Metternich hosted; the British Foreign Secretary '
                'Castlereagh provided ballast; [[alexander-i]] supplied ambition.\n\n'
                '## Principles\n\n'
                'The Congress operated on three principles: legitimacy (restoring '
                'lawful sovereigns), balance of power (no single state should '
                'dominate), and compensation (victorious powers received territory '
                'as reward). France, represented brilliantly by [[talleyrand]], '
                'avoided dismemberment.\n\n'
                '## Alexander\'s Vision\n\n'
                'The tsar [[alexander-i]] proposed the Holy Alliance — a league of '
                'Christian monarchs pledging to govern by Christian principles. '
                'Most European leaders signed, though Castlereagh privately called '
                'it "a piece of sublime mysticism and nonsense." The Congress '
                'settlement held, with modifications, until 1848 — and the European '
                'Concert it created influenced diplomacy until 1914.'
            ),
        },
    ],
}


def _make_relationship(from_type, from_slug, to_type, to_slug, rel_type,
                       description='', strength=3, bidirectional=False):
    return {
        'from_type': from_type, 'from_slug': from_slug,
        'to_type': to_type, 'to_slug': to_slug,
        'rel_type': rel_type, 'description': description,
        'strength': strength, 'bidirectional': bidirectional,
    }


INTRA_ERA_RELATIONSHIPS = [
    # French Revolution
    _make_relationship('person', 'louis-xvi', 'event', 'bastille-1789', 'was_affected_by',
                       'The storming of the Bastille ended Louis XVI\'s absolute power.', 5),
    _make_relationship('person', 'louis-xvi', 'event', 'execution-of-louis-xvi', 'ended',
                       'Louis XVI was executed by guillotine.', 5),
    _make_relationship('person', 'marie-antoinette', 'person', 'louis-xvi', 'spouse',
                       'Marie Antoinette and Louis XVI were married in 1770.', 5, True),
    _make_relationship('person', 'maximilien-robespierre', 'event', 'reign-of-terror', 'led',
                       'Robespierre dominated the Committee of Public Safety during the Terror.', 5),
    _make_relationship('person', 'marquis-de-lafayette', 'event', 'declaration-rights-of-man', 'led',
                       'Lafayette drafted the Declaration of the Rights of Man.', 4),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'coup-18-brumaire', 'led',
                       'Napoleon organized and led the coup that ended the Revolution.', 5),
    _make_relationship('person', 'georges-danton', 'person', 'maximilien-robespierre', 'rival',
                       'Danton\'s calls for clemency made him Robespierre\'s enemy.', 4),

    # Napoleonic Era
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'battle-of-austerlitz', 'led',
                       'Napoleon\'s tactical masterpiece — his greatest victory.', 5),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'invasion-of-russia-1812', 'led',
                       'Napoleon commanded the Grande Armée\'s catastrophic Russian campaign.', 5),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'battle-of-waterloo', 'was_affected_by',
                       'Napoleon was defeated at Waterloo, ending his rule permanently.', 5),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'napoleon-crowned-emperor', 'defined',
                       'Napoleon crowned himself Emperor of the French in Notre-Dame.', 5),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'hundred-days', 'led',
                       'Napoleon escaped Elba and ruled France for 111 days.', 4),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'battle-of-nations-leipzig', 'was_affected_by',
                       'Napoleon was decisively defeated at Leipzig, ending French hegemony.', 5),
    _make_relationship('person', 'napoleon-bonaparte', 'person', 'josephine-de-beauharnais', 'spouse',
                       'Napoleon and Joséphine were married 1796–1809, divorced over succession.', 4, True),
    _make_relationship('person', 'napoleon-bonaparte', 'person', 'talleyrand', 'advisor',
                       'Talleyrand served as Napoleon\'s Foreign Minister 1799–1807.', 4),
    _make_relationship('person', 'napoleon-bonaparte', 'person', 'marshal-michel-ney', 'ally',
                       'Ney was Napoleon\'s finest combat marshal, "the bravest of the brave."', 5),
    _make_relationship('person', 'duke-of-wellington', 'event', 'battle-of-waterloo', 'led',
                       'Wellington commanded the Allied forces that defeated Napoleon.', 5),
    _make_relationship('person', 'marshal-michel-ney', 'event', 'invasion-of-russia-1812', 'survived',
                       'Ney commanded the rearguard and was the last French soldier to leave Russia.', 5),
    _make_relationship('person', 'marshal-michel-ney', 'event', 'hundred-days', 'participated',
                       'Ney rejoined Napoleon during the Hundred Days despite promising Louis XVIII otherwise.', 4),
    _make_relationship('person', 'talleyrand', 'event', 'congress-of-vienna', 'led',
                       'Talleyrand represented France at Vienna and secured its equal standing.', 5),
    _make_relationship('event', 'battle-of-trafalgar', 'event', 'battle-of-austerlitz', 'was_affected_by',
                       'Trafalgar (October) and Austerlitz (December 1805) shaped opposite ends of Napoleon\'s power.', 3),
    _make_relationship('event', 'invasion-of-russia-1812', 'event', 'battle-of-borodino', 'caused',
                       'Borodino was the central battle of the Russian invasion.', 4),
    _make_relationship('event', 'invasion-of-russia-1812', 'event', 'battle-of-nations-leipzig', 'caused',
                       'The Russian disaster weakened France enough to enable the coalition\'s Leipzig campaign.', 5),
]

# Cross-era relationships to Romanov Dynasty entities
CROSS_ERA_RELATIONSHIPS = [
    _make_relationship('person', 'napoleon-bonaparte', 'person', 'alexander-i', 'rival',
                       'Napoleon and Alexander I were the defining rivalry of the era, '
                       'from Austerlitz (1805) to the Congress of Vienna (1814).', 5, True),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'battle-of-austerlitz', 'led', '', 5),
    _make_relationship('person', 'alexander-i', 'event', 'battle-of-austerlitz', 'was_affected_by',
                       'Alexander I was present at Austerlitz and was personally humiliated by defeat.', 5),
    _make_relationship('person', 'alexander-i', 'event', 'invasion-of-russia-1812', 'was_affected_by',
                       'Alexander I refused to negotiate with Napoleon, driving the French to catastrophe.', 5),
    _make_relationship('person', 'alexander-i', 'event', 'battle-of-nations-leipzig', 'led',
                       'Alexander I was the driving political force behind the coalition at Leipzig.', 5),
    _make_relationship('person', 'alexander-i', 'event', 'congress-of-vienna', 'led',
                       'Alexander I was the dominant figure at the Congress of Vienna.', 5),
    _make_relationship('person', 'napoleon-bonaparte', 'event', 'coup-18-brumaire', 'led', '', 5),
]


def _resolve(type_name, slug):
    model_map = {'person': Person, 'event': Event, 'period': Period, 'era': Era}
    model = model_map.get(type_name)
    if not model:
        return None, None
    try:
        obj = model.objects.get(slug=slug)
        ct = ContentType.objects.get_for_model(model)
        return ct, obj.pk
    except model.DoesNotExist:
        return None, None


class Command(BaseCommand):
    help = 'Seeds the French Revolution and Napoleonic Era eras with full content'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Update existing records instead of skipping')

    def handle(self, *args, **options):
        force = options['force']
        created_eras = {}
        created_periods = {}

        # ── Eras ──
        for era_data in ERAS:
            slug = era_data['slug']
            era, created = Era.objects.get_or_create(
                slug=slug, defaults=era_data
            )
            if not created and force:
                Era.objects.filter(slug=slug).update(
                    **{k: v for k, v in era_data.items() if k != 'slug'}
                )
                era.refresh_from_db()
            created_eras[slug] = era
            self.stdout.write(f"{'Created' if created else 'Exists'}: Era — {era.name}")

        # ── Periods ──
        for era_slug, period_list in PERIODS.items():
            era = created_eras[era_slug]
            for pd in period_list:
                slug = pd['slug']
                defaults = {**pd, 'era': era}
                period, created = Period.objects.get_or_create(
                    slug=slug, defaults=defaults
                )
                if not created and force:
                    Period.objects.filter(slug=slug).update(
                        **{k: v for k, v in defaults.items() if k != 'slug'}
                    )
                    period.refresh_from_db()
                created_periods[slug] = period
                self.stdout.write(f"  {'Created' if created else 'Exists'}: Period — {period.name}")

        # ── People ──
        created_people = {}
        for era_slug, person_list in PEOPLE.items():
            era = created_eras[era_slug]
            for p in person_list:
                slug = p['slug']
                period_slug = p.pop('period_slug', None)
                defaults = {
                    **p,
                    'era': era,
                    'period': created_periods.get(period_slug),
                    'status': 'published',
                }
                person, created = Person.objects.get_or_create(
                    slug=slug, defaults={**defaults, 'slug': slug}
                )
                if not created and force:
                    Person.objects.filter(slug=slug).update(
                        **{k: v for k, v in defaults.items() if k not in ('tags',)}
                    )
                    person.refresh_from_db()
                created_people[slug] = person
                self.stdout.write(
                    f"  {'Created' if created else 'Exists'}: {person.name}"
                )

        # ── Events ──
        for era_slug, event_list in EVENTS.items():
            era = created_eras[era_slug]
            for e in event_list:
                slug = e['slug']
                period_slug = e.pop('period_slug', None)
                defaults = {
                    **e,
                    'era': era,
                    'period': created_periods.get(period_slug),
                    'status': 'published',
                }
                event, created = Event.objects.get_or_create(
                    slug=slug, defaults={**defaults, 'slug': slug}
                )
                if not created and force:
                    Event.objects.filter(slug=slug).update(
                        **{k: v for k, v in defaults.items() if k not in ('tags',)}
                    )
                    event.refresh_from_db()
                self.stdout.write(
                    f"  {'Created' if created else 'Exists'}: {event.year} — {event.name}"
                )

        # ── Relationships (intra-era + cross-era) ──
        rel_count = 0
        all_rels = INTRA_ERA_RELATIONSHIPS + CROSS_ERA_RELATIONSHIPS
        for rel in all_rels:
            from_ct, from_id = _resolve(rel['from_type'], rel['from_slug'])
            to_ct, to_id = _resolve(rel['to_type'], rel['to_slug'])
            if not from_ct or not to_ct:
                self.stdout.write(self.style.WARNING(
                    f"  SKIP: {rel['from_slug']} → {rel['to_slug']} (entity not found)"
                ))
                continue
            _, created = Relationship.objects.get_or_create(
                from_entity_type=from_ct, from_entity_id=from_id,
                to_entity_type=to_ct, to_entity_id=to_id,
                relationship_type=rel['rel_type'],
                defaults={
                    'description': rel.get('description', ''),
                    'strength': rel.get('strength', 3),
                    'is_bidirectional': rel.get('bidirectional', False),
                }
            )
            if created:
                rel_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Created {rel_count} relationships.'
        ))
        self.stdout.write(
            'Next: uv run python manage.py fetch_images  (to pull Wikipedia portraits)'
        )
