"""
One-time script to write all knowledge base chunks into rag/knowledge/.
Run: python rag/seed_knowledge.py
"""

import os

OUT = os.path.join(os.path.dirname(__file__), "knowledge")
os.makedirs(OUT, exist_ok=True)

CHUNKS = {
    # ── CDC — TINEA ───────────────────────────────────────────────────────────
    "cdc_tinea_01.txt": """SOURCE: CDC
TOPIC: What is Ringworm (Tinea)
---
Ringworm is a common fungal infection of the skin caused by dermatophytes — a group of fungi that feed on keratin, the protein found in skin, hair, and nails. Despite its name, ringworm has nothing to do with worms. The infection is called ringworm because it can cause a ring-shaped rash on the skin.

Ringworm can affect different parts of the body. When it occurs on the body, it is called tinea corporis. When it affects the scalp, it is called tinea capitis. Tinea pedis refers to athlete's foot, and tinea cruris refers to jock itch.

The infection is very common worldwide and affects people of all ages. It is more prevalent in warm, humid climates where the fungi thrive. Children are particularly susceptible to tinea capitis. People who participate in contact sports, use communal showers, or have close contact with infected animals are at higher risk.

Ringworm spreads through direct skin-to-skin contact with an infected person or animal. It can also spread by touching contaminated objects such as towels, clothing, or bedding. The fungi can survive on surfaces for extended periods, making indirect transmission possible.

Most cases of ringworm can be treated effectively with over-the-counter antifungal medications. Severe or widespread infections may require prescription antifungal treatment.
""",
    "cdc_tinea_02.txt": """SOURCE: CDC
TOPIC: Ringworm Symptoms and Signs
---
The symptoms of ringworm vary depending on the location of the infection on the body. On the skin (tinea corporis), ringworm typically appears as a ring-shaped, scaly rash. The outer edge of the rash is usually raised, red, and scaly, while the center may appear normal or slightly discolored.

The rash may be itchy and uncomfortable. As the infection spreads, the ring may grow larger. Multiple rings can appear and sometimes overlap. The skin inside the ring may appear clearer than the surrounding skin. In some cases, the rash does not form a perfect ring and instead appears as an irregular scaly patch.

On the scalp (tinea capitis), ringworm causes scaly, itchy, bald patches. The affected area may appear dotted with black specks where hair has broken off at the scalp surface. In some cases, a raised, spongy, inflammatory mass called a kerion can form.

On the feet (tinea pedis or athlete's foot), symptoms include scaling, flaking, and itching of the affected skin. The skin between toes is commonly affected first. Blisters and sores may develop in severe cases.

On the nails (tinea unguium), nails become thick, discolored, brittle, and may separate from the nail bed.

Early recognition of ringworm symptoms allows prompt treatment, which reduces the risk of spreading the infection to others.
""",
    "cdc_tinea_03.txt": """SOURCE: CDC
TOPIC: Ringworm Treatment
---
Most ringworm infections can be treated effectively with antifungal medications. The choice of treatment depends on the location and severity of the infection.

For ringworm on the skin (tinea corporis), over-the-counter antifungal creams, lotions, or powders are usually effective. Common active ingredients include clotrimazole, miconazole, terbinafine, and tolnaftate. These should be applied to the affected area and the surrounding skin according to package directions, typically for two to four weeks, even if symptoms improve before the full course is completed.

For tinea capitis (scalp ringworm), topical antifungals alone are generally not effective because the infection is within the hair shaft. Oral antifungal medication such as griseofulvin or terbinafine is required. Treatment typically lasts six to twelve weeks. Antifungal shampoos may be used alongside oral treatment to reduce shedding of fungal spores.

For widespread or stubborn infections that do not respond to over-the-counter treatments, a doctor may prescribe stronger prescription antifungal medications.

During treatment, it is important to keep the affected area clean and dry. Wash clothing, towels, and bedding regularly. Avoid sharing personal items. Continue treatment for the full recommended duration to prevent recurrence. Most people see improvement within one to two weeks of starting treatment, but the full course must be completed.
""",
    "cdc_tinea_04.txt": """SOURCE: CDC
TOPIC: Ringworm Prevention
---
Ringworm is highly contagious and can spread easily from person to person and from animals to people. However, several measures can reduce the risk of infection.

Practice good hygiene by washing hands thoroughly with soap and water after touching animals, soil, or other people. Shower promptly after contact sports or gym workouts. Keep skin clean and dry, as fungi thrive in warm, moist environments.

Avoid sharing personal items such as clothing, towels, hairbrushes, or sports equipment. Use footwear such as sandals or flip-flops in communal areas like locker rooms, showers, and swimming pools.

Treat infected animals promptly. Pets such as dogs and cats can carry ringworm and transmit it to people. If a pet has bald, scaly patches, consult a veterinarian.

In school settings, children with scalp ringworm should be treated before returning to school to prevent spread to classmates. Children with body ringworm can usually attend school once treatment has begun.

Keep sports equipment and uniforms clean. Inspect the skin of wrestlers and other contact sport athletes regularly for signs of infection. Treat infected athletes immediately and exclude them from competition until the infection is controlled.

In communities with high rates of ringworm, awareness campaigns about hygiene practices can help reduce transmission. Education about early recognition and prompt treatment is particularly important in high-risk settings.
""",
    "cdc_tinea_05.txt": """SOURCE: CDC
TOPIC: Ringworm Risk Factors and Vulnerable Populations
---
Certain groups of people are more likely to develop ringworm infections. Understanding risk factors helps target prevention efforts.

Children are particularly vulnerable to scalp ringworm (tinea capitis). School-age children between three and fourteen years are most commonly affected. Close contact in schools and daycares facilitates transmission.

Athletes who participate in contact sports such as wrestling are at elevated risk of tinea corporis, sometimes called tinea gladiatorum. Direct skin contact during sports facilitates transmission. Shared equipment and locker room facilities further increase risk.

People who work with animals, particularly farmers, veterinarians, and pet owners, have higher exposure to zoophilic dermatophytes that can cause ringworm.

Individuals who live in or travel to tropical or subtropical regions are at higher risk due to warm, humid conditions that favor fungal growth. This is particularly relevant in countries like Bangladesh where heat and humidity are constant environmental factors.

People with weakened immune systems due to HIV infection, cancer treatment, or immunosuppressive drugs may develop more severe or widespread ringworm infections.

Obesity and diabetes increase susceptibility to fungal skin infections. Poor nutrition and overcrowded living conditions also increase risk.

Close household contacts of infected individuals should be examined and treated if infected. Education about transmission routes and hygiene is important for households with multiple affected members.
""",

    # ── CDC — SCABIES ─────────────────────────────────────────────────────────
    "cdc_scabies_01.txt": """SOURCE: CDC
TOPIC: What is Scabies
---
Scabies is a skin infestation caused by a tiny, eight-legged mite called Sarcoptes scabiei. The mite burrows into the outer layer of human skin to live and lay eggs. Scabies is found worldwide and affects people of all races, ages, and socioeconomic levels. It can spread rapidly in crowded conditions such as hospitals, childcare facilities, prisons, and refugee camps.

The female scabies mite burrows into the skin and deposits eggs. The eggs hatch into larvae in three to four days. The larvae migrate to the skin surface and develop into adult mites. The entire life cycle takes about ten to seventeen days. Mites can live for one to two months on a person, but die within two to three days if they fall off the host.

Scabies is most commonly transmitted by prolonged, direct, skin-to-skin contact with a person who has scabies. Contact must be prolonged; a brief handshake or hug is usually not sufficient to spread scabies. However, transmission may occur more quickly between individuals who have intimate physical contact.

Scabies may also be transmitted indirectly by sharing clothing, towels, or bedding with an infested person, although this is less common for typical scabies. Crusted (Norwegian) scabies can be transmitted through brief contact or via contaminated items.

Scabies is not a sign of poor hygiene. Anyone can get scabies regardless of cleanliness. Prompt treatment of all household members and sexual partners is essential to prevent re-infestation.
""",
    "cdc_scabies_02.txt": """SOURCE: CDC
TOPIC: Scabies Symptoms
---
The most common symptom of scabies is intense itching, which is often worse at night and after a hot bath. The itching is caused by an allergic reaction to the mites, their eggs, and their waste products.

A rash consisting of small, raised bumps (papules) is another hallmark of scabies. The rash is often accompanied by tiny blisters and scales. Scratching can cause the skin to break, leading to secondary bacterial infections.

The scabies mite has a preference for certain areas of the body. Common sites include the webbing between fingers, wrists, elbows, armpits, the area around the waist and navel, buttocks, genital area in men, and areas around the nipples in women. In infants and young children, the head, face, neck, palms, and soles may also be affected.

Burrows, which appear as tiny, grayish-white or skin-colored tracks of about five to fifteen millimeters in length, are the most characteristic sign of scabies. These represent tunnels dug by the female mite. Burrows are most commonly found between fingers, on the wrists, and on the penis.

Symptoms typically develop within two to six weeks of infestation in people who have never had scabies before. In people who have previously had scabies, symptoms can develop within one to four days of re-exposure because the immune system is already sensitized.

A person with crusted (Norwegian) scabies may have thick, crusted skin containing thousands of mites. The intense itching typical of common scabies may be absent in crusted scabies.
""",
    "cdc_scabies_03.txt": """SOURCE: CDC
TOPIC: Scabies Treatment
---
Scabies is treated with prescription medications called scabicides that kill the scabies mites. No over-the-counter products have been proven safe and effective for treating scabies.

The most commonly prescribed scabicides include permethrin cream (five percent), which is considered first-line treatment and is safe for use in adults, pregnant women, and children aged two months and older. The cream is applied from the neck down (head and neck included in infants and young children), left on for eight to fourteen hours, then washed off.

Ivermectin is an oral medication used for patients who cannot tolerate topical treatments, those with crusted scabies, or in outbreaks in institutional settings. It is given as a single dose and often repeated in two weeks.

All household members and sexual contacts should be treated simultaneously, even if they show no symptoms, to prevent re-infestation. Treatment failures often occur when all contacts are not treated at the same time.

Clothing, bedding, and towels used by infested persons in the three days before treatment should be decontaminated by machine washing in hot water and drying in a hot dryer. Items that cannot be washed should be placed in a sealed plastic bag for seventy-two hours.

Itching may persist for two to four weeks after successful treatment due to the ongoing allergic reaction to dead mites. Persistence of burrows or new tracks appearing after one to two weeks may indicate treatment failure or re-infestation.
""",
    "cdc_scabies_04.txt": """SOURCE: CDC
TOPIC: Scabies Prevention and Control
---
Preventing scabies involves avoiding prolonged direct skin contact with persons who have scabies. Sexual partners and household contacts of infested individuals should be treated simultaneously.

In institutional settings such as nursing homes, hospitals, and childcare centers, prompt identification and treatment of infested individuals is essential. All residents and staff who have had prolonged contact with an infested person should be treated at the same time to prevent ongoing transmission.

Cleaning and decontamination of the environment is an important part of scabies control. Wash all clothing, towels, and bedding used by infested persons in the previous three days in hot water and dry on a high heat setting. Items that cannot be washed should be sealed in a plastic bag for at least seventy-two hours, as mites cannot survive more than two to three days away from a human host.

Do not use fumigants or pesticides to spray or fog homes, rooms, or furniture. These measures are not necessary and are potentially toxic.

In communities with high scabies burden, mass drug administration (MDA) with ivermectin has been used to reduce prevalence. WHO recommends MDA as a strategy for scabies control in highly endemic communities.

Public education about scabies transmission, symptoms, and treatment helps reduce stigma and encourages early treatment. Scabies is not related to poor hygiene. Anyone can become infested.
""",
    "cdc_scabies_05.txt": """SOURCE: CDC
TOPIC: Crusted (Norwegian) Scabies
---
Crusted scabies, also called Norwegian scabies, is a severe form of scabies in which thousands to millions of mites infest the skin. It is much more contagious than typical scabies and can be spread through brief contact or contaminated surfaces.

Crusted scabies typically occurs in people with weakened immune systems, such as those with HIV infection, those receiving immunosuppressive therapy, elderly individuals in nursing homes, or people with physical or mental disabilities that limit scratching. People with crusted scabies may not experience the intense itching that characterizes typical scabies.

The skin in crusted scabies develops thick, grayish crusts that are teeming with mites and eggs. The crusts can be widespread, covering large areas of the body including the scalp, face, neck, and hands. The crusts crumble easily and shed infected skin scales.

Treatment of crusted scabies is more intensive than typical scabies. Multiple applications of permethrin cream (applied daily for a week, then twice weekly until cured) combined with oral ivermectin given in multiple doses are usually required. A keratolytic agent may be used to remove crusts before applying scabicide.

Isolation of hospitalized patients with crusted scabies is recommended. Healthcare workers providing care should wear gloves and gowns and wash hands thoroughly. All contacts must be treated simultaneously.

Without proper treatment, crusted scabies can persist for years and represents a significant source of scabies transmission in institutional settings and communities.
""",

    # ── CDC — ATOPIC DERMATITIS ───────────────────────────────────────────────
    "cdc_atopic_dermatitis_01.txt": """SOURCE: CDC
TOPIC: What is Atopic Dermatitis
---
Atopic dermatitis, commonly known as eczema, is a chronic inflammatory skin condition characterized by dry, itchy, inflamed skin. It is the most common form of eczema and typically begins in childhood, though it can occur at any age. Atopic dermatitis often occurs alongside other atopic conditions such as asthma and allergic rhinitis, a group sometimes called the atopic triad.

The condition affects approximately ten to twenty percent of children and two to five percent of adults worldwide. It is more prevalent in urban areas and industrialized countries, though incidence is rising in developing nations as well.

Atopic dermatitis results from a combination of genetic and environmental factors. A defect in the skin barrier function allows allergens and irritants to penetrate the skin more easily, triggering immune responses. People with atopic dermatitis often have mutations in the gene encoding filaggrin, a protein essential for skin barrier integrity.

The immune system plays a central role in atopic dermatitis. The condition involves both an overactivation of the immune system and an impaired skin barrier, creating a cycle of inflammation, itching, scratching, and further skin damage.

Atopic dermatitis is characterized by periods of flares, during which symptoms worsen, and periods of remission, during which symptoms improve or clear. Common triggers for flares include dry skin, sweating, stress, certain soaps and detergents, dust mites, pet dander, certain foods, and changes in temperature or humidity.

While there is no cure, atopic dermatitis can be effectively managed with appropriate treatment and lifestyle modifications.
""",
    "cdc_atopic_dermatitis_02.txt": """SOURCE: CDC
TOPIC: Atopic Dermatitis Symptoms
---
The main symptom of atopic dermatitis is dry, intensely itchy skin. The itching can be severe, often worse at night, and significantly disrupts sleep quality and daily activities. Scratching provides only temporary relief and worsens the skin damage.

The appearance of atopic dermatitis varies depending on the age of the affected person and the stage of the condition. In infants, the rash often appears on the face, particularly the cheeks and chin, and on the scalp. It can spread to the arms and legs. The rash appears as red, oozing, crusting patches.

In children, the rash typically moves to the creases of the elbows and knees, the neck, the wrists, and around the eyes and mouth. The skin may become thickened, leathery, or darkened (lichenification) from chronic scratching.

In adults, the rash is more likely to cover a larger area of the body, with particularly severe involvement of the face, neck, hands, and the creases of the elbows and knees. The skin may be very dry, scaly, and thickened.

Common features include dry, sensitive skin; red to brownish-gray patches; small, raised bumps that may weep fluid when scratched; thickened, cracked, or scaly skin; and raw, swollen skin from scratching.

Atopic dermatitis increases susceptibility to skin infections, particularly with Staphylococcus aureus bacteria and herpes simplex virus. Secondary infections can cause yellow crusting, increased redness, and fever.

The psychological impact of atopic dermatitis is significant. Chronic itch, sleep disruption, and visible skin changes can lead to anxiety, depression, and reduced quality of life.
""",
    "cdc_atopic_dermatitis_03.txt": """SOURCE: CDC
TOPIC: Atopic Dermatitis Treatment and Management
---
While there is no cure for atopic dermatitis, effective treatments can control symptoms and reduce flares. A comprehensive management plan includes skincare routines, avoidance of triggers, and medical treatments.

Moisturization is the cornerstone of atopic dermatitis management. Apply thick moisturizers such as creams or ointments to damp skin immediately after bathing. This helps restore the skin barrier and prevent dryness. Avoid fragranced products, which can irritate sensitive skin.

Topical corticosteroids are the most commonly prescribed medications for atopic dermatitis flares. They reduce inflammation and relieve itching. They are available in different strengths and should be used as directed by a healthcare provider. Prolonged use of potent corticosteroids can cause skin thinning.

Topical calcineurin inhibitors (tacrolimus and pimecrolimus) are non-steroidal alternatives that are particularly useful for sensitive areas such as the face and skin folds.

For moderate to severe atopic dermatitis that does not respond to topical treatments, systemic medications may be required. These include dupilumab, a biologic injection that specifically targets the immune pathways involved in atopic dermatitis, as well as oral corticosteroids, cyclosporine, and methotrexate.

Wet wrap therapy, in which moisturizer or topical medication is applied and then covered with wet bandages, can provide relief during severe flares.

Antihistamines may help reduce nighttime itching and improve sleep. Antibiotics are prescribed when secondary bacterial infection is present.

Identifying and avoiding personal triggers is essential for long-term management. Common triggers include certain fabrics, soaps, detergents, stress, sweating, extreme temperatures, and specific allergens.
""",

    # ── CDC — ECZEMA ──────────────────────────────────────────────────────────
    "cdc_eczema_01.txt": """SOURCE: CDC
TOPIC: Types of Eczema
---
Eczema is a general term for a group of conditions that cause the skin to become inflamed, itchy, red, and irritated. There are several distinct types of eczema, each with different causes and characteristics.

Atopic dermatitis is the most common type and is often associated with asthma and hay fever. It typically begins in childhood and involves periods of flares and remission.

Contact dermatitis occurs when the skin comes into contact with an irritant or allergen. Irritant contact dermatitis results from direct damage to the skin by a chemical substance such as detergents, bleach, or industrial chemicals. Allergic contact dermatitis is an immune-mediated reaction to a specific allergen such as nickel, latex, or poison ivy.

Dyshidrotic eczema causes small, itchy blisters on the edges of the fingers, toes, palms, and soles of the feet. It is associated with stress, seasonal allergies, and exposure to certain metals.

Nummular eczema appears as circular or coin-shaped patches of irritated skin. It is often triggered by very dry skin, insect bites, or skin injuries.

Seborrheic dermatitis primarily affects the scalp, causing scaly patches, red skin, and stubborn dandruff. It also affects oily areas of the body such as the face and chest.

Stasis dermatitis develops when poor circulation in the legs causes fluid to leak from veins into the skin. It typically affects older adults.

Neurodermatitis (lichen simplex chronicus) begins with a patch of itchy skin that becomes leathery and thick from repeated scratching.

Understanding the specific type of eczema is essential for appropriate treatment and management strategies.
""",
    "cdc_eczema_02.txt": """SOURCE: CDC
TOPIC: Eczema Triggers and Management
---
Eczema symptoms are often triggered by environmental factors and lifestyle choices. Identifying and avoiding personal triggers is a key component of eczema management.

Common eczema triggers include dry skin, which is both a symptom and a trigger; irritants such as soaps, detergents, shampoos, disinfectants, and certain fabrics like wool or synthetic fibers; allergens including dust mites, pet dander, pollen, and mold; foods such as dairy products, eggs, nuts, wheat, and soy (particularly relevant in children); temperature changes, especially heat and sweating; stress and emotional factors; hormonal changes in women; and certain medications.

Managing eczema involves both treating acute flares and preventing new ones. Daily bathing in lukewarm water followed by immediate moisturizer application helps maintain skin barrier function. Use mild, unscented soaps and avoid bubble baths.

Wear loose-fitting, soft, natural-fiber clothing. Avoid scratching, which worsens inflammation and increases infection risk. Keep fingernails short and smooth. Consider cotton gloves at night to prevent scratching during sleep.

Maintain a comfortable home environment with moderate temperature and humidity. Use air conditioning or fans to reduce sweating. Vacuum regularly to reduce dust mite exposure. Consider hypoallergenic bedding.

Stress management is important as psychological stress can trigger and worsen eczema flares. Techniques such as mindfulness, yoga, and adequate sleep can help.

For infants with eczema, identify and eliminate food triggers through an elimination diet under medical supervision. Breastfeeding may reduce eczema risk in high-risk infants.
""",
    "cdc_eczema_03.txt": """SOURCE: CDC
TOPIC: Eczema in Children
---
Eczema is particularly common in children, affecting up to twenty percent of children worldwide. It typically begins in infancy, with many children developing symptoms before their first birthday.

In infants, eczema usually appears as a red, weeping, crusting rash on the cheeks, chin, scalp, and forehead. The rash can spread to other areas of the body. Infants with eczema are extremely uncomfortable due to the intense itch. Scratching can lead to skin infections.

As children grow, the rash pattern typically shifts to the creases of the elbows and knees, the wrists, and the ankles. Skin may become thickened and dry with repeated inflammation.

Many children with eczema have the condition as part of the atopic march — a progression that often begins with eczema in infancy, followed by food allergies, asthma, and allergic rhinitis as the child grows.

Management of eczema in children requires a team approach involving the child, parents, and healthcare providers. Daily moisturizer application is essential. Identify and avoid personal triggers. Use mild, fragrance-free products for bathing and laundry.

Topical corticosteroids are the primary treatment for flares in children. Strength and duration should be guided by a healthcare provider to avoid side effects from prolonged use. Topical calcineurin inhibitors are used in children aged two years and older.

Eczema can significantly affect a child's quality of life. Sleep disruption from nighttime itching, school absences, and the psychological burden of a visible skin condition can impact development and social interaction. Family support and education are important components of management.

Many children experience significant improvement or resolution of eczema by adolescence, though some continue to have the condition into adulthood.
""",

    # ── CDC — CONTACT DERMATITIS ──────────────────────────────────────────────
    "cdc_contact_dermatitis_01.txt": """SOURCE: CDC
TOPIC: Contact Dermatitis — Overview and Types
---
Contact dermatitis is inflammation of the skin that occurs when the skin comes into contact with a substance that causes irritation or an allergic reaction. It is one of the most common occupational skin diseases and affects millions of people worldwide.

There are two main types of contact dermatitis. Irritant contact dermatitis is the most common type and accounts for approximately eighty percent of cases. It results from direct damage to the skin by a chemical substance. The reaction occurs at the site of contact and begins within minutes to hours of exposure. Common irritants include water, soaps, detergents, cleaning products, solvents, acids, alkalis, and friction.

Allergic contact dermatitis is an immune-mediated reaction that occurs in individuals who have become sensitized to a particular substance. Sensitization requires at least one prior exposure. Subsequent exposures trigger an immune response that causes inflammation. Allergic contact dermatitis typically develops twelve to seventy-two hours after exposure. Common allergens include nickel (found in jewelry and belt buckles), latex rubber, fragrances, preservatives in cosmetics and personal care products, hair dyes containing paraphenylenediamine (PPD), poison ivy and related plants, and certain medications applied to the skin.

A third type, photocontact dermatitis, occurs when a substance on the skin is activated by sunlight to cause irritation or an allergic reaction.

Risk factors for contact dermatitis include occupation (healthcare workers, hairdressers, construction workers, and food handlers are at high risk), history of atopic dermatitis, and frequent hand washing or exposure to water.
""",
    "cdc_contact_dermatitis_02.txt": """SOURCE: CDC
TOPIC: Contact Dermatitis Symptoms and Treatment
---
Symptoms of contact dermatitis appear at the site where the skin came into contact with the triggering substance. The rash is usually well-defined and limited to the exposed area, which helps distinguish it from other types of eczema.

In acute contact dermatitis, symptoms include redness, swelling, itching, blistering, and oozing of the affected skin. The rash can be intensely itchy and uncomfortable. In more severe allergic reactions, the rash may spread beyond the area of direct contact.

In chronic contact dermatitis due to repeated exposure, the skin becomes dry, thickened, scaly, and cracked. The affected skin may develop a leathery texture (lichenification). Hyperpigmentation or hypopigmentation may occur in some individuals.

The most important treatment for contact dermatitis is identifying and avoiding the triggering substance. Patch testing performed by a dermatologist can identify specific allergens causing allergic contact dermatitis.

During an acute flare, treatment includes rinsing the affected area with cool water to remove the triggering substance, applying cool compresses to relieve itching and weeping, and using topical corticosteroids to reduce inflammation. Oral antihistamines can help relieve itching.

For severe reactions, oral corticosteroids may be prescribed for a short course. Secondary bacterial infections require antibiotic treatment.

Prevention involves identifying and consistently avoiding known triggers. Use protective equipment such as gloves when handling irritants. Choose fragrance-free, hypoallergenic personal care and household products. Moisturize regularly to maintain the skin barrier.
""",

    # ── CDC — SEBORRHEIC DERMATITIS ───────────────────────────────────────────
    "cdc_seborrheic_dermatitis_01.txt": """SOURCE: CDC
TOPIC: Seborrheic Dermatitis Overview
---
Seborrheic dermatitis is a common skin condition that mainly affects the scalp, causing scaly patches, red skin, and stubborn dandruff. It can also affect oily areas of the body such as the face, sides of the nose, eyebrows, ears, eyelids, and chest.

The condition is chronic, with periods of flares and remission. It is not contagious and is not caused by poor hygiene. The exact cause of seborrheic dermatitis is not fully understood, but it is believed to involve an abnormal response to the Malassezia yeast that naturally lives on the skin surface.

Seborrheic dermatitis is most common in infants (where it is called cradle cap), adolescents and young adults during hormonal changes, and in older adults. The condition affects up to five percent of the general population worldwide.

Several factors can trigger or worsen seborrheic dermatitis. These include stress, fatigue, extreme weather, infrequent washing, oily skin, and neurological conditions such as Parkinson's disease. People with HIV infection have a higher prevalence and often more severe seborrheic dermatitis. Certain medications including lithium, psoralen, and some interferon treatments can trigger the condition.

In infants, cradle cap appears as thick, yellowish, greasy scales on the scalp. It usually clears on its own within a few months and is not itchy or uncomfortable for the infant.

In adults, symptoms include flaking skin (dandruff) on the scalp or hair, patches of greasy skin covered with white or yellowish scales, red skin, and itching. The scalp is most commonly affected, but the beard, mustache, eyebrows, the folds around the nose, and ears can also be involved.
""",
    "cdc_seborrheic_dermatitis_02.txt": """SOURCE: CDC
TOPIC: Seborrheic Dermatitis Treatment
---
Seborrheic dermatitis is a chronic condition that typically requires ongoing management. Treatment aims to control symptoms and reduce flares.

For scalp seborrheic dermatitis, medicated shampoos are the first-line treatment. Over-the-counter antifungal shampoos containing ketoconazole, selenium sulfide, zinc pyrithione, or coal tar are effective for many people. These should be used regularly as directed and may need to be alternated to prevent resistance.

For maintenance, use medicated shampoo at least once or twice a week. Leave the shampoo on the scalp for five minutes before rinsing to maximize effectiveness. Alternate with a regular mild shampoo on other days.

For facial and body seborrheic dermatitis, topical antifungal creams containing ketoconazole or ciclopirox are effective. Topical corticosteroids help reduce inflammation during flares but should not be used continuously on the face due to the risk of skin thinning.

Topical calcineurin inhibitors (tacrolimus or pimecrolimus) are useful alternatives for treating seborrheic dermatitis on the face, as they do not cause skin thinning.

In cases where topical treatments are insufficient, oral antifungal medications may be prescribed.

Lifestyle measures that can help manage seborrheic dermatitis include managing stress, getting adequate sleep, washing hair and face regularly, avoiding products that contain alcohol which can dry and irritate skin, and using gentle, fragrance-free skin care products.

Regular treatment is important because seborrheic dermatitis tends to recur. Most people need to continue some form of treatment indefinitely to keep the condition under control.
""",

    # ── CDC — VITILIGO ────────────────────────────────────────────────────────
    "cdc_vitiligo_01.txt": """SOURCE: CDC
TOPIC: What is Vitiligo
---
Vitiligo is a chronic skin condition in which patches of skin lose their pigment, resulting in white or light-colored patches. The condition occurs when melanocytes — the cells responsible for producing skin pigment (melanin) — are destroyed or stop functioning. Vitiligo can affect any area of the body, including the skin, hair, and the mucous membranes inside the mouth and nose.

Vitiligo affects approximately one to two percent of the world's population. It occurs equally in males and females and can affect people of all skin types and ethnicities, though it is more noticeable in people with darker skin.

The exact cause of vitiligo is not fully understood, but it is generally considered to be an autoimmune condition in which the immune system mistakenly attacks and destroys melanocytes. Genetic factors play a role, as vitiligo tends to run in families. About twenty to thirty percent of people with vitiligo have a family member with the condition.

Vitiligo may also be associated with other autoimmune conditions including thyroid disease, type 1 diabetes, rheumatoid arthritis, lupus, and pernicious anemia.

There are different patterns of vitiligo. Generalized vitiligo is the most common form, with depigmented patches appearing on many different areas of the body. Segmental vitiligo affects only one side of the body and tends to be more stable. Focal vitiligo is limited to one or a few small areas.

Vitiligo can begin at any age, but often starts before age thirty. The condition is typically progressive, with depigmentation spreading over time, though the rate of progression varies greatly between individuals.
""",
    "cdc_vitiligo_02.txt": """SOURCE: CDC
TOPIC: Vitiligo Treatment and Psychological Impact
---
While there is no cure for vitiligo, several treatments can help restore skin color or slow the progression of depigmentation. Treatment choice depends on the extent and location of patches, skin type, patient preference, and response to therapy.

Topical corticosteroids can help restore skin color, particularly when vitiligo is limited in extent and the condition is in early stages. They should be used under medical supervision to avoid side effects.

Topical calcineurin inhibitors (tacrolimus and pimecrolimus) are effective and safe alternatives to corticosteroids, particularly for facial and neck vitiligo.

Phototherapy using ultraviolet light is one of the most effective treatments for widespread vitiligo. Narrowband UVB phototherapy is the most commonly used form. Treatment requires multiple sessions per week over months.

Newer targeted therapies include ruxolitinib cream, a JAK inhibitor that has shown significant effectiveness in restoring pigmentation in clinical trials.

Surgical options such as skin grafting and melanocyte transplantation are available for stable vitiligo that has not responded to other treatments.

Cosmetic approaches including camouflage makeup, self-tanning products, and micropigmentation (tattooing) can help conceal patches.

The psychological impact of vitiligo can be profound, particularly in societies where skin appearance is closely linked to social acceptance and marriage prospects. People with vitiligo, especially in South Asian countries including Bangladesh, often face significant social stigma, discrimination, and difficulty in marriage. Anxiety and depression are common.

Counseling and support groups are important components of comprehensive vitiligo care. Public education to reduce stigma is particularly important in high-burden communities.
""",

    # ── NIH — TINEA ───────────────────────────────────────────────────────────
    "nih_tinea_01.txt": """SOURCE: NIH
TOPIC: Tinea Infections — Clinical Overview
---
Tinea infections, caused by dermatophytes, represent some of the most common fungal infections in humans. Dermatophytes are a specialized group of fungi that require keratin for growth and can only infect keratinized tissues including skin, hair, and nails. The three main genera responsible for tinea infections are Trichophyton, Microsporum, and Epidermophyton.

Tinea infections are classified by the body site affected. Tinea corporis (body), tinea capitis (scalp), tinea pedis (feet), tinea cruris (groin), tinea unguium (nails), and tinea manuum (hands) are the most common forms.

The clinical presentation of tinea depends on the specific dermatophyte species and the host immune response. The classic presentation is an annular (ring-shaped) lesion with a raised, scaly, erythematous border and central clearing. However, the presentation can be variable, especially in immunocompromised hosts who may develop more widespread and atypical infections.

Diagnosis is often made clinically based on characteristic morphology and location. Laboratory confirmation can be obtained through potassium hydroxide (KOH) examination of skin scrapings, which reveals fungal hyphae under microscopy. Fungal culture on Sabouraud dextrose agar confirms the diagnosis and identifies the specific species, which guides treatment decisions.

Wood's lamp examination causes certain species of Microsporum to fluoresce green, which can be useful in scalp tinea diagnosis, though many dermatophyte species do not fluoresce.

Treatment with topical antifungals is effective for most superficial tinea infections. Systemic therapy is required for tinea capitis, tinea unguium, and extensive or recalcitrant infections.
""",
    "nih_tinea_02.txt": """SOURCE: NIH
TOPIC: When to Seek Medical Care for Tinea
---
Most superficial tinea infections can be managed with over-the-counter antifungal treatments. However, certain situations require medical evaluation and treatment.

Seek medical care if the rash does not improve after two weeks of over-the-counter antifungal treatment, if the rash involves the scalp or nails (these require prescription oral antifungal medications), if there are signs of secondary bacterial infection such as increased redness, warmth, swelling, pus, or fever, if the rash is widespread or covers large areas of the body, or if the person is immunocompromised.

Children with suspected scalp ringworm should be evaluated by a healthcare provider promptly. Tinea capitis requires oral antifungal therapy (typically griseofulvin or terbinafine) and does not respond to topical treatment alone. Without proper treatment, tinea capitis can cause permanent hair loss.

A kerion — a boggy, inflammatory mass on the scalp — is a severe complication of tinea capitis requiring urgent medical treatment. It can cause permanent scarring and hair loss if not treated promptly.

Tinea of the nails (onychomycosis) is difficult to treat and requires long-term oral antifungal therapy. Diagnosis should be confirmed by laboratory testing before beginning treatment, as other nail conditions can mimic fungal infection.

Recurrent tinea infections may indicate an underlying condition that predisposes to fungal infection, such as diabetes, HIV infection, or prolonged corticosteroid use. Evaluation for these underlying conditions is appropriate when tinea recurs frequently.

In Bangladesh and other tropical countries, tinea is endemic. Any spreading, ring-shaped rash should be evaluated promptly to prevent widespread skin involvement.
""",
    "nih_tinea_03.txt": """SOURCE: NIH
TOPIC: Tinea — Antifungal Medications
---
A range of antifungal medications is available for treating tinea infections. Selection depends on the type and severity of infection, the site of involvement, and patient factors.

Topical antifungals are the first-line treatment for uncomplicated tinea of the body (tinea corporis) and other superficial infections. These include azole antifungals such as clotrimazole, miconazole, econazole, and ketoconazole; allylamines such as terbinafine and naftifine; and other agents such as ciclopirox and tolnaftate. Allylamine antifungals (terbinafine) generally require shorter treatment durations than azoles.

Application should continue for one to two weeks after visible resolution to prevent recurrence. Stopping treatment too early is a common cause of relapse.

Oral antifungals are necessary for tinea capitis, onychomycosis, tinea affecting hair follicles (tinea barbae), and extensive or recalcitrant tinea corporis. Griseofulvin has been used for decades for tinea capitis. Terbinafine and itraconazole are newer oral antifungals with broad activity and shorter treatment courses.

For tinea capitis in children, terbinafine dosed by weight for four weeks or griseofulvin for six to twelve weeks are standard regimens.

For onychomycosis (nail tinea), oral terbinafine for twelve weeks (toenails) or six weeks (fingernails) achieves cure rates of approximately seventy-five percent for toenails.

Drug interactions and potential hepatotoxicity with oral antifungals require consideration. Liver function monitoring is recommended for prolonged courses.

In resource-limited settings including rural Bangladesh, clotrimazole and miconazole creams are widely available and affordable, making them appropriate first-line choices for uncomplicated tinea.
""",

    # ── NIH — SCABIES ────────────────────────────────────────────────────────
    "nih_scabies_01.txt": """SOURCE: NIH
TOPIC: Scabies — Clinical Diagnosis
---
The diagnosis of scabies is primarily clinical, based on the characteristic history of intense pruritus (especially nocturnal), typical distribution of the rash, and the presence of burrows. Confirmation by identifying the mite, its eggs, or feces (scybala) under dermoscopy or microscopy strengthens the diagnosis.

Dermoscopy (dermatoscopy) has emerged as a useful non-invasive tool for diagnosing scabies. The scabies mite appears under dermoscopy as a triangular brown structure at the end of a burrow — sometimes described as a jet plane with its contrail.

For microscopic confirmation, skin scrapings taken from a burrow are examined under microscopy after treatment with mineral oil or potassium hydroxide. The presence of mites, eggs, or scybala confirms the diagnosis.

The distribution of rash and burrows varies by age. In adults and older children, the genitals, interdigital spaces, wrists, axillae, umbilical area, and buttocks are classic sites. In infants and young children, involvement of the palms, soles, face, and scalp is common and helps distinguish pediatric from adult scabies.

Serological tests and skin tests have limited utility in routine clinical practice. Polymerase chain reaction (PCR) techniques for scabies mite DNA show promise for diagnosis in research settings.

The differential diagnosis of scabies includes other itchy skin conditions such as atopic dermatitis, contact dermatitis, insect bites, pityriasis rosea, and secondary syphilis. The simultaneous occurrence of similar symptoms in multiple household members strongly suggests scabies.

Post-scabetic itch persisting after successful treatment is due to hypersensitivity to remaining mite antigens and does not indicate treatment failure. This commonly leads to unnecessary retreatment.
""",
    "nih_scabies_02.txt": """SOURCE: NIH
TOPIC: Scabies in Children and Households
---
Scabies in children presents with features distinct from adult infection. Infants and young children are more likely to have involvement of the face, scalp, palms, and soles — areas usually spared in adults. The rash may be more vesicular and pustular in young children.

Infants with scabies are often profoundly irritable, especially at night when pruritus worsens. Feeding difficulties, sleep disturbance, and failure to thrive can result from severe infestation. Parents often seek medical care believing the child has eczema or another skin condition.

Secondary impetiginization (bacterial superinfection) with Streptococcus pyogenes or Staphylococcus aureus is common in children with scabies, particularly in tropical settings. In some regions, scabies-associated streptococcal infection is a significant cause of post-streptococcal glomerulonephritis (kidney disease).

Treatment of scabies must encompass all household members simultaneously, regardless of whether they have symptoms. Treating only symptomatic individuals leads to rapid re-infestation because asymptomatic contacts can transmit the mite.

Permethrin five percent cream is safe for infants aged two months and older. For neonates and infants younger than two months, consultation with a specialist is recommended. Ivermectin can be used in children weighing fifteen kilograms or more.

Practical challenges to effective household treatment in resource-limited settings include cost of medication, large household size, and difficulty ensuring all members are treated at once. Community education and mass treatment programs may be more effective in highly endemic settings.

Post-treatment follow-up at two weeks is recommended to assess treatment response and identify retreatment needs.
""",

    # ── NIH — ATOPIC DERMATITIS / ECZEMA ─────────────────────────────────────
    "nih_atopic_dermatitis_01.txt": """SOURCE: NIH
TOPIC: Atopic Dermatitis — Pathophysiology and Skin Barrier
---
The understanding of atopic dermatitis (AD) has advanced significantly with the recognition that skin barrier dysfunction is central to the disease. The skin barrier normally prevents water loss from the body (transepidermal water loss, TEWL) and blocks entry of environmental allergens, irritants, and microorganisms.

In atopic dermatitis, the skin barrier is functionally impaired. Loss-of-function mutations in the FLG gene, which encodes the protein filaggrin, are the strongest known genetic risk factor for atopic dermatitis. Filaggrin is essential for forming the cornified cell envelope and maintaining skin barrier integrity.

With a defective skin barrier, water evaporates more readily from the skin, causing chronic dryness. Allergens, irritants, and microorganisms penetrate more easily, triggering immune activation. The resulting immune response involves activation of T helper type 2 (Th2) cells, which produce inflammatory cytokines including interleukin-4 (IL-4), IL-5, and IL-13.

Staphylococcus aureus colonizes the skin of more than ninety percent of people with moderate to severe atopic dermatitis. Staphylococcal toxins act as superantigens, amplifying the immune response and worsening inflammation. They also promote IgE sensitization to skin-associated allergens.

The itch-scratch cycle is central to disease perpetuation. Scratching damages the skin barrier further, worsens inflammation, and creates portals for infection. Controlling itch is therefore a central therapeutic goal.

Understanding these mechanisms has led to targeted biological therapies. Dupilumab, which blocks the IL-4 and IL-13 pathways, represents a major advance in the treatment of moderate to severe atopic dermatitis.
""",
    "nih_eczema_01.txt": """SOURCE: NIH
TOPIC: Living with Eczema — Daily Management
---
Living with eczema requires ongoing attention to skincare, trigger avoidance, and adherence to treatment plans. Developing effective daily habits can significantly reduce the frequency and severity of flares.

Bathing practices are important for eczema management. Take short, lukewarm baths or showers — hot water removes natural oils from the skin and worsens dryness. Use mild, unscented soap. Pat skin gently dry after bathing rather than rubbing. Apply moisturizer within three minutes of getting out of the bath or shower to lock in moisture.

Choosing appropriate skincare products is essential. Use fragrance-free, dye-free moisturizers, soaps, laundry detergents, and household cleaners. Ointments and thick creams are generally more effective moisturizers than lotions. Petroleum jelly (Vaseline) is an inexpensive and effective option.

Clothing choices affect eczema. Wear soft, breathable fabrics such as cotton and avoid rough, scratchy materials like wool. Wash new clothing before wearing to remove excess dye and preservatives. Use fragrance-free, hypoallergenic laundry detergent.

Environmental controls help reduce exposure to triggers. Keep the home cool and humid. Use a humidifier during dry seasons. Vacuum regularly and use dust-mite-proof mattress and pillow covers. Keep pets out of the bedroom.

Stress management is often overlooked but critically important. Psychological stress is a well-recognized trigger for eczema flares. Regular exercise, adequate sleep, relaxation techniques, and mental health support can reduce stress-related flares.

Develop a written eczema action plan with your healthcare provider that specifies what to do when symptoms are mild, moderate, or severe. Regular follow-up appointments allow treatment adjustment as needed.
""",

    # ── NIH — CONTACT DERMATITIS ──────────────────────────────────────────────
    "nih_contact_dermatitis_01.txt": """SOURCE: NIH
TOPIC: Contact Dermatitis — Diagnosis and Patch Testing
---
Accurate diagnosis of contact dermatitis, particularly the allergic type, is important for effective management. The history is paramount, including details of occupation, hobbies, personal care product use, jewelry wearing habits, and any new exposures that preceded rash onset.

The location and pattern of the rash provide important clues. A rash on the earlobes, neck, and wrists suggests nickel allergy. A rash on the feet may indicate allergy to shoe materials. Rash around the eyes may result from nail cosmetics transferred from the fingers. An unusual or unexpected pattern warrants careful exploration of indirect exposures.

Patch testing is the gold standard for identifying specific allergens causing allergic contact dermatitis. Standardized panels of common allergens are applied to the back under occlusive patches for forty-eight hours. Readings are performed at forty-eight and ninety-six hours. Positive reactions appear as redness, swelling, or vesicles at the site of the allergen.

Common allergens identified through patch testing include metals (nickel, cobalt, chromate), fragrances (fragrance mix I and II, balsam of Peru), preservatives (methylisothiazolinone, parabens, formaldehyde releasers), rubber chemicals, hair dye components (paraphenylenediamine), and topical medications (neomycin, bacitracin).

Once the causative allergen is identified, written information about sources of exposure and safe alternatives should be provided. Avoiding the specific allergen is the definitive treatment.

In occupational contact dermatitis, workplace assessment may be needed to identify all sources of exposure and implement substitutions or protective measures. Workers compensation and occupational health support may be relevant.
""",

    # ── NIH — SEBORRHEIC DERMATITIS ───────────────────────────────────────────
    "nih_seborrheic_dermatitis_01.txt": """SOURCE: NIH
TOPIC: Seborrheic Dermatitis and Malassezia
---
The pathogenesis of seborrheic dermatitis involves an interplay between Malassezia yeast, sebum production, and host immune response. Malassezia species, particularly Malassezia globosa and Malassezia restricta, are lipophilic yeasts that naturally colonize human skin in sebum-rich areas.

In susceptible individuals, Malassezia produces lipases that break down sebum triglycerides into free fatty acids. These free fatty acids — particularly oleic acid — penetrate the skin barrier and trigger inflammation, disrupting the skin barrier further and causing the scaling and redness characteristic of seborrheic dermatitis.

Sebum production increases during puberty, which explains why seborrheic dermatitis is common in adolescents. Sebaceous gland activity declines in old age, but seborrheic dermatitis can still occur. The scalp, face, and chest have the highest density of sebaceous glands, explaining the preferential distribution.

The host immune response to Malassezia varies between individuals. People who develop seborrheic dermatitis appear to have an exaggerated inflammatory response to normal levels of Malassezia colonization. Immunocompromised individuals, particularly those with HIV infection or receiving immunosuppressive therapy, can develop severe and widespread seborrheic dermatitis.

Neurological associations of seborrheic dermatitis are well-established. The condition is significantly more common and severe in people with Parkinson's disease. Elevated sebum production due to autonomic dysfunction and impaired facial expression leading to sebum accumulation are proposed mechanisms.

Antifungal treatments that reduce Malassezia load are effective for seborrheic dermatitis, confirming the central role of the yeast in disease pathogenesis.
""",

    # ── NIH — VITILIGO ────────────────────────────────────────────────────────
    "nih_vitiligo_01.txt": """SOURCE: NIH
TOPIC: Vitiligo — Autoimmune Mechanisms and Genetics
---
Vitiligo is now understood to be primarily an autoimmune disease in which cytotoxic T lymphocytes (CD8+ T cells) destroy melanocytes in the skin and hair follicles. This immune-mediated destruction leads to the characteristic depigmented patches.

The interferon-gamma (IFN-γ) signaling pathway plays a central role in vitiligo pathogenesis. IFN-γ produced by autoreactive T cells activates the JAK-STAT signaling pathway in keratinocytes, which promotes CXCL9 and CXCL10 chemokine production. These chemokines recruit additional T cells to the skin, amplifying melanocyte destruction.

This mechanistic understanding has led to the development of JAK inhibitor treatments for vitiligo. Ruxolitinib cream (a topical JAK inhibitor) has received FDA approval for vitiligo, demonstrating that targeted immunotherapy can restore pigmentation.

Genetic studies have identified over fifty genetic loci associated with vitiligo risk. Many of these genes are involved in immune regulation, melanocyte biology, or apoptosis. Genes shared between vitiligo and other autoimmune conditions (such as PTPN22, CTLA4, and HLA region variants) confirm the autoimmune nature of vitiligo.

Environmental factors that may trigger vitiligo in genetically susceptible individuals include psychological stress, sunburn, physical trauma to the skin (Koebner phenomenon), certain chemical exposures, and viral infections.

Thyroid autoimmunity is the most commonly associated condition in people with vitiligo. Up to thirty percent of vitiligo patients have thyroid antibodies. Screening for thyroid disease is recommended, particularly in women and those with extensive vitiligo.

Understanding the autoimmune mechanisms opens new avenues for therapeutic intervention beyond cosmetic treatment.
""",
    "nih_vitiligo_02.txt": """SOURCE: NIH
TOPIC: Vitiligo — Living with the Condition
---
Vitiligo is a visible condition that can significantly affect quality of life, particularly in individuals with darker skin tones where the contrast between affected and unaffected skin is more pronounced.

The psychological impact of vitiligo is well-documented. Studies consistently show higher rates of depression, anxiety, low self-esteem, and social withdrawal among individuals with vitiligo compared to the general population. Body image disturbance and feelings of shame are particularly common. Vitiligo on the face and hands — visible areas that are difficult to conceal — causes the greatest psychological burden.

In many cultures, including those of South Asia, vitiligo carries significant social stigma. In Bangladesh and other South Asian countries, vitiligo is sometimes confused with leprosy or considered a sign of sin or impurity, leading to social exclusion and discrimination in marriage and employment.

Sun protection is important for people with vitiligo. Depigmented skin lacks melanin protection against ultraviolet radiation, making it much more susceptible to sunburn. Regular use of broad-spectrum sunscreen (SPF 30 or higher) on depigmented patches is recommended.

Cosmetic camouflage using specially formulated waterproof concealers can effectively cover vitiligo patches and improve confidence and social functioning. Self-tanning products and skin-tone correctors are alternative approaches.

Support from mental health professionals, peer support groups, and patient advocacy organizations is an important component of comprehensive vitiligo care. Healthcare providers should routinely assess the psychological impact and refer appropriately.

Public awareness campaigns are essential to reduce stigma and misinformation about vitiligo in communities where misconceptions are prevalent.
""",

    # ── WHO — SCABIES ────────────────────────────────────────────────────────
    "who_scabies_01.txt": """SOURCE: WHO
TOPIC: Scabies as a Neglected Tropical Disease
---
Scabies is included in the World Health Organization's list of neglected tropical diseases (NTDs). It is estimated that at any given time, more than two hundred million people worldwide are affected by scabies. The global burden is highest in tropical and resource-limited settings in sub-Saharan Africa, South and Southeast Asia, and the Pacific Islands.

Scabies affects all ages but is particularly burdensome for children and the elderly. In many endemic communities, scabies prevalence can exceed fifty percent among children. The condition causes significant morbidity through intense pruritus that disrupts sleep and daily activities.

Beyond the direct impact of infestation, scabies carries serious secondary health consequences. Secondary bacterial infection with Streptococcus pyogenes and Staphylococcus aureus is extremely common, particularly in tropical settings. Streptococcal skin infections can lead to post-streptococcal glomerulonephritis (kidney disease) and rheumatic fever, contributing to significant morbidity and mortality.

The economic burden of scabies in endemic communities is substantial. Lost workdays due to illness, costs of treatment, and reduced school attendance by affected children have measurable impacts on household and community productivity.

WHO's 2030 NTD Road Map targets the global control of scabies, with a focus on reducing its prevalence in endemic areas and preventing the serious complications of secondary bacterial infection. The strategy includes mass drug administration (MDA) with ivermectin in highly endemic communities, strengthened surveillance, and integration of scabies control into primary health care systems.

Bangladesh, with its dense population, tropical climate, and high rates of poverty in rural areas, bears a significant scabies burden, particularly among children in rural and peri-urban communities.
""",
    "who_scabies_02.txt": """SOURCE: WHO
TOPIC: WHO Guidelines for Scabies Treatment
---
The World Health Organization recommends two primary treatments for scabies: topical permethrin five percent cream and oral ivermectin.

Permethrin five percent cream is the preferred first-line topical treatment for scabies based on its safety profile, efficacy, and availability. It is applied to the entire skin surface from the neck down (including the scalp and face in infants and young children) and left in place for eight to twelve hours before washing off. A second application one week later is often recommended.

Oral ivermectin is recommended for the treatment of individual cases of scabies, household contacts, and as the cornerstone of mass drug administration programs for community control. The standard dose is two hundred micrograms per kilogram body weight given as a single oral dose, repeated after one week. Ivermectin is not recommended for children weighing less than fifteen kilograms or for pregnant women, for whom permethrin remains the preferred option.

WHO supports mass drug administration (MDA) with ivermectin as a strategy for scabies control in communities where prevalence exceeds ten percent. MDA targets the entire community simultaneously, including individuals without visible symptoms, to break the transmission cycle. Studies in Pacific Island communities have demonstrated dramatic reductions in scabies prevalence following MDA campaigns.

Alternative topical treatments that may be used in resource-limited settings where permethrin is not available include benzyl benzoate twenty-five percent lotion and sulfur five to ten percent ointment. These are less effective and more irritating than permethrin but are used in some settings due to lower cost.

Simultaneous treatment of all household members and sexual contacts is essential regardless of the treatment approach used. Washing of clothing and bedding should accompany treatment.
""",
    "who_tinea_01.txt": """SOURCE: WHO
TOPIC: WHO and Dermatophytosis (Tinea) Global Burden
---
Dermatophytosis (tinea infections) represents the most prevalent group of human fungal infections globally. The World Health Organization recognizes dermatophytosis as a significant public health problem, particularly in tropical and subtropical regions.

The global prevalence of tinea infections is estimated at fifteen to twenty-five percent of the population, making them among the most common infectious diseases. Tinea pedis (athlete's foot) is the most common form worldwide, affecting up to twenty percent of adults. Tinea unguium (nail infection) affects approximately ten percent of the global population.

In tropical regions including Bangladesh, tinea corporis, tinea capitis in children, and tinea cruris are particularly prevalent. The warm, humid climate creates ideal conditions for dermatophyte growth and transmission. Communal bathing facilities, shared towels, and overcrowding in households contribute to high transmission rates.

Tinea capitis remains a significant public health concern in school-age children in tropical countries. Outbreaks in schools can affect large proportions of children. Untreated tinea capitis can cause permanent scarring and hair loss (alopecia), with lasting impact on children's appearance and self-esteem.

WHO promotes integration of dermatophytosis treatment into primary health care. Affordable, effective antifungal treatments are available and should be accessible to all affected populations. Clotrimazole cream, widely available in Bangladesh's upazila health complexes and pharmacies, is effective for most superficial tinea infections.

The economic burden of tinea infections in tropical countries is significant, accounting for lost productivity and healthcare expenditures. Scaling up access to affordable antifungal medications and improving community hygiene are public health priorities.
""",
    "who_atopic_dermatitis_01.txt": """SOURCE: WHO
TOPIC: WHO Perspective on Atopic Dermatitis Global Burden
---
Atopic dermatitis is recognized as a significant global public health problem by the World Health Organization. The condition affects an estimated two hundred thirty million people worldwide, including up to twenty percent of children in high-income countries and between two and ten percent of children in low- and middle-income countries.

The incidence of atopic dermatitis has increased substantially in recent decades, particularly in developing countries undergoing urbanization and lifestyle changes. The hygiene hypothesis proposes that reduced early childhood exposure to infections and microorganisms associated with modern urban lifestyles leads to inappropriate immune development and increased susceptibility to allergic conditions.

Environmental factors driving the rise of atopic dermatitis in developing countries include increased air pollution, changes in diet, reduced biodiversity of skin and gut microbiomes, and increased exposure to chemical irritants. Climate change may further increase disease burden by intensifying temperature extremes and altering aeroallergen patterns.

The burden of atopic dermatitis extends beyond the affected individual. Caregivers of children with atopic dermatitis experience significant psychological distress, sleep disruption, and economic burden. The cost of medical care, lost productivity, and reduced quality of life constitute substantial societal costs.

WHO promotes a comprehensive approach to managing atopic dermatitis that includes accessible basic skincare education, availability of affordable moisturizers and topical corticosteroids, and integration of mental health support.

In countries like Bangladesh, the dual challenge of tropical climate (promoting dryness and irritation through sweating followed by evaporative cooling) and limited access to specialist dermatology care creates a significant unmet need for accessible, effective atopic dermatitis management.
""",
    "who_skin_diseases_01.txt": """SOURCE: WHO
TOPIC: WHO Skin Diseases in South and Southeast Asia
---
Skin diseases represent a disproportionate burden in South and Southeast Asia, including Bangladesh, due to a combination of tropical climate, population density, limited healthcare access, and socioeconomic factors.

The World Health Organization estimates that skin diseases account for nearly thirty percent of all outpatient consultations in primary healthcare settings in tropical countries. Despite their high prevalence, many skin conditions receive inadequate attention in public health planning.

Common skin diseases in the region include fungal infections (tinea, pityriasis versicolor), scabies, bacterial infections (impetigo, cellulitis), eczema, contact dermatitis, leprosy (though declining), and pigmentary disorders including vitiligo.

The ratio of dermatologists to population in South Asian countries is extremely low. In Bangladesh, there is approximately one dermatologist per two hundred fifty thousand people. The vast majority of skin disease patients are seen by general practitioners, community health workers, or traditional healers, many of whom have limited dermatology training.

Misdiagnosis and inappropriate treatment are common. Many patients with scabies are treated for eczema, and vice versa. Antifungal treatments are often inadequate in duration. Reliance on traditional remedies or unlicensed practitioners leads to delayed effective treatment.

WHO supports integration of basic skin disease management into primary healthcare curricula and training programs. The essential medicines list includes permethrin, clotrimazole, topical corticosteroids, and ivermectin — all relevant to common skin diseases in the region.

Task-sharing and training of community health workers in basic skin disease recognition and management is a WHO-recommended strategy for closing the healthcare gap in underserved regions.
""",
    "who_vitiligo_01.txt": """SOURCE: WHO
TOPIC: Vitiligo — Global Stigma and Public Health Implications
---
Vitiligo presents unique public health challenges related to its visible nature, association with significant social stigma, and the need for long-term management. While not life-threatening, vitiligo can have severe impacts on quality of life and mental health, particularly in societies where skin appearance carries social importance.

In South Asian countries, including Bangladesh, India, and Pakistan, vitiligo is often confused with leprosy — a condition that historically carried profound social stigma. This confusion leads to unnecessary fear, social exclusion, and discrimination against people with vitiligo. Marriage prospects can be severely affected, particularly for women, where vitiligo is sometimes grounds for rejection or divorce.

The World Health Organization recognizes the mental health dimension of skin conditions, including vitiligo. Psychological distress, depression, and anxiety associated with vitiligo can be as disabling as many physically debilitating conditions.

WHO advocates for destigmatization of skin conditions through public education, community awareness programs, and integration of mental health support into dermatological care. Addressing misinformation about vitiligo being contagious or related to leprosy is a priority in South Asian public health messaging.

Healthcare systems in low- and middle-income countries should ensure that people with vitiligo have access to accurate diagnosis, appropriate management, and psychological support. Training primary healthcare workers to distinguish vitiligo from leprosy and other conditions is important.

The economic impact of vitiligo through employment discrimination and reduced social participation represents a measurable but often overlooked public health burden in countries like Bangladesh.
""",
    "who_scabies_community_01.txt": """SOURCE: WHO
TOPIC: Community Management of Scabies
---
Community-level approaches to scabies control are essential in endemic areas where household-level treatment alone is insufficient to break transmission chains.

Mass drug administration (MDA) with oral ivermectin has transformed scabies control in several Pacific Island nations. Studies in Fiji, Vanuatu, and the Solomon Islands have shown that community-wide treatment of all residents, regardless of symptom status, can reduce scabies prevalence from fifty percent or higher to less than two percent within twelve months.

WHO recommends a three-tier approach to scabies control: reactive treatment (treating individual cases and contacts), enhanced reactive treatment (treating entire households of cases), and proactive MDA (treating entire communities when prevalence exceeds ten percent).

Community health education is an essential component of all scabies control programs. Key messages include that scabies is caused by a mite — not poor hygiene; that all household members must be treated simultaneously; that itching may persist for several weeks after successful treatment; and that bedding and clothing must be washed on the day of treatment.

Integration of scabies management into national neglected tropical disease programs allows more efficient use of resources and coordination with other MDA programs such as lymphatic filariasis and soil-transmitted helminthiasis.

In Bangladesh, community health workers (community health assistants and health inspectors) play a vital role in identifying and managing scabies at the household and community level. Strengthening their capacity to recognize and appropriately manage scabies, and ensuring community access to permethrin cream and ivermectin through the upazila health system, is essential for scabies control.
""",

    # ── DGHS BANGLADESH ───────────────────────────────────────────────────────
    "dghs_tinea_bd_01.txt": """SOURCE: DGHS
TOPIC: Tinea Infections in Bangladesh — Epidemiology and Context
---
Tinea infections (dermatophytosis) are among the most common skin conditions encountered in primary healthcare settings across Bangladesh. The country's tropical climate, characterized by high temperature and humidity year-round, creates optimal conditions for dermatophyte growth and transmission.

Tinea corporis (ringworm of the body) and tinea cruris (jock itch) are prevalent throughout the country. Tinea capitis is particularly common among school-age children in rural areas, where communal living conditions, shared personal items, and limited access to healthcare contribute to spread.

Agricultural workers are at particularly high risk of tinea infections due to prolonged exposure to warm, moist conditions and contact with soil and animals. Farmers working in rice paddy fields spend extended periods in warm, wet conditions that predispose to tinea pedis and tinea cruris.

In Bangladesh, many tinea cases go untreated or are managed by unqualified practitioners who may prescribe inappropriate treatments. Steroid-modified tinea (tinea incognito) — tinea treated with topical corticosteroids that alters the appearance and makes diagnosis difficult — is increasingly recognized as a significant problem.

The Directorate General of Health Services (DGHS) of Bangladesh includes antifungal medications in the essential drug list provided at upazila health complexes and community clinics throughout the country. Clotrimazole cream is available at these facilities for treatment of uncomplicated tinea.

Public health education about tinea — including that it is caused by fungus, not worms; that it is treated with antifungal medications, not steroids; and that it can be prevented through hygiene measures — is an important component of primary health outreach in Bangladesh.
""",
    "dghs_scabies_bd_01.txt": """SOURCE: DGHS
TOPIC: Scabies Burden and Management in Bangladesh
---
Scabies is a significant public health problem in Bangladesh, particularly in rural areas and among the economically disadvantaged. The country's tropical climate, high population density, overcrowded housing conditions, and limited access to healthcare create conditions that favor scabies transmission.

Studies from Bangladesh have reported scabies prevalence rates of fifteen to forty percent in rural children and higher rates in slum communities and institutional settings such as madrasas (Islamic schools with boarding facilities). Scabies in these settings can spread rapidly and affect large proportions of students.

Secondary bacterial infection complicating scabies — particularly with Streptococcus pyogenes — is common in Bangladesh and contributes to the burden of impetigo, cellulitis, and post-streptococcal glomerulonephritis.

The Directorate General of Health Services (DGHS) includes permethrin five percent cream in treatment protocols for scabies at upazila health complexes. Community health workers — including community health assistants (CHAs) and health assistants — are trained to recognize and refer scabies cases.

Challenges to scabies control in Bangladesh include poverty limiting ability to purchase treatment for all household members; lack of hot water facilities for laundering bedding in rural homes; large family sizes making simultaneous household treatment difficult; insufficient awareness among families about the need to treat all household members simultaneously; and limited availability of permethrin in remote areas.

National health programs in Bangladesh should integrate scabies control with broader NTD management. Mass drug administration with ivermectin, following the WHO model, could significantly reduce scabies burden in highly endemic communities in Bangladesh.
""",
    "dghs_eczema_bd_01.txt": """SOURCE: DGHS
TOPIC: Eczema and Atopic Dermatitis in Bangladesh
---
Atopic dermatitis and eczema are increasingly recognized as significant contributors to skin disease burden in Bangladesh. While historically considered primarily diseases of high-income countries, the incidence of atopic conditions is rising in developing nations including Bangladesh.

The changing epidemiology of atopic dermatitis in Bangladesh is driven by rapid urbanization, changing lifestyles, increased exposure to environmental pollutants, and dietary changes. Urban children in Dhaka and other major cities appear to have higher rates of atopic dermatitis than rural children, consistent with the hygiene hypothesis.

Bangladesh's climate presents unique challenges for eczema management. The hot, humid climate promotes sweating, which irritates sensitive skin and triggers flares. During the cool, dry winter months, low humidity causes increased skin dryness, another common trigger.

Seasonal variation in eczema severity is commonly reported by patients in Bangladesh. Flares are frequent during seasonal transitions, particularly at the onset of the summer monsoon season and during the dry winter months.

Common triggers identified by Bangladeshi eczema patients include sweating, dust exposure, changes in temperature, certain foods (particularly dairy), and synthetic fabrics worn in the heat. Wool, unavailable for most of the year due to the climate, is a less common trigger than in temperate countries.

The Directorate General of Health Services Bangladesh recognizes atopic dermatitis as a significant outpatient condition. Upazila health complexes have access to topical corticosteroids (particularly hydrocortisone and betamethasone creams) for treatment of eczema flares. Emollients are less consistently available but are recommended in national treatment guidelines.

Patient education about moisturizer use, trigger avoidance, and appropriate use of topical corticosteroids is a priority for community health outreach in Bangladesh.
""",
    "dghs_vitiligo_bd_01.txt": """SOURCE: DGHS
TOPIC: Vitiligo in Bangladesh — Social Stigma and Healthcare Approach
---
Vitiligo represents a significant psychosocial burden in Bangladesh, where the condition carries substantial social stigma. The visible nature of vitiligo, combined with deeply held cultural beliefs about skin appearance, creates severe consequences for affected individuals and their families.

In Bangladesh, vitiligo is often confused with leprosy by community members, leading to unwarranted fear and social exclusion. Despite awareness campaigns, this misperception persists in rural communities. People with vitiligo have reported being avoided in public spaces, excluded from social gatherings, and discriminated against in schools and workplaces.

The impact on marriage is particularly severe. In Bangladesh's predominantly arranged marriage system, vitiligo — especially in women — is frequently grounds for rejection of marriage proposals. Affected women may feel compelled to conceal the condition before marriage, causing significant psychological distress. Divorce following discovery of vitiligo has been reported.

The economic impact is also significant. Social discrimination in employment, combined with the costs of cosmetic concealment and medical treatment, creates measurable financial burdens for affected individuals and families.

Directorate General of Health Services Bangladesh recognizes vitiligo as a medical condition requiring both dermatological and psychological management. Doctors at district hospitals and medical college hospitals provide consultation, phototherapy (where equipment is available), and referral for specialist care.

Community education campaigns conducted by DGHS and NGO partners aim to clarify that vitiligo is not leprosy, not contagious, not caused by any moral failing, and that it is a treatable autoimmune condition. Destigmatization is a public health priority.

Healthcare workers at all levels should be able to distinguish vitiligo from other pigmentary disorders and leprosy, and should be equipped to provide counseling and referral.
""",
    "dghs_skin_referral_01.txt": """SOURCE: DGHS
TOPIC: Skin Disease Referral Pathways in Bangladesh Health System
---
Bangladesh's tiered health system provides a structured pathway for managing skin disease patients, from community-level recognition through specialist referral.

At the community level, community health assistants (CHAs) and health assistants conduct household visits and provide basic health education. They are trained to recognize common skin conditions including scabies, tinea, and impetigo, and to refer patients requiring treatment to the nearest community clinic or upazila health complex.

Community clinics, located at the union level, provide the first formal healthcare contact for many rural patients with skin conditions. General practitioners at community clinics can manage common skin conditions including scabies (with permethrin cream), uncomplicated tinea (with clotrimazole cream), and mild eczema (with topical corticosteroids). Essential medicines for these conditions are provided through DGHS supply chains.

Upazila health complexes (UHC) serve as the referral center for cases beyond community clinic capacity. UHCs have medical officers who can manage more complex skin conditions. Patients with severe, widespread, or treatment-resistant skin disease, suspected severe infections, or conditions requiring systemic treatment should be referred to UHC.

District hospitals have specialist physicians including medical officers with dermatology training. They manage complex conditions such as severe atopic dermatitis, widespread scabies outbreaks, and skin disease in immunocompromised patients.

Medical college hospitals in divisional cities (Dhaka, Chittagong, Rajshahi, Khulna, Sylhet, Mymensingh, Barishal) have dermatology departments with consultants who manage severe and complex cases including phototherapy for vitiligo and psoriasis, and inpatient management of severe skin disease.

The goal of the referral system is to ensure appropriate care at the right level — preventing unnecessary referral of simple cases while ensuring complex cases reach specialist care.
""",
    "dghs_rural_skin_01.txt": """SOURCE: DGHS
TOPIC: Skin Diseases in Rural Bangladesh — Burden and Challenges
---
Rural Bangladesh faces a disproportionate burden of skin disease due to a combination of occupational, environmental, social, and health system factors.

Agricultural occupations prevalent in rural Bangladesh — particularly rice cultivation, which involves prolonged standing in water — create significant risk for skin conditions including tinea pedis, tinea cruris, contact dermatitis from agrochemicals, and secondary bacterial infections. Pesticide and fertilizer exposure among farmers contributes to contact dermatitis.

Poor sanitation and limited access to clean water in rural areas facilitate transmission of infectious skin diseases including scabies, tinea, and impetigo. Overcrowded households — common in rural Bangladesh — accelerate spread within families.

Limited access to dermatology services is a major challenge. The vast majority of dermatologists practice in Dhaka and other urban centers. Rural patients may travel for four to six hours to reach a dermatologist. The cost of transportation, consultation fees, and medications places specialist care beyond reach for many rural families.

As a result, many rural patients first seek care from village doctors (unqualified practitioners), pharmacists, or traditional healers. Inappropriate treatment — including misuse of topical corticosteroids for tinea infections, which worsens the condition — is common.

The Directorate General of Health Services works to address these challenges through upazila health system strengthening, training of healthcare workers in dermatology basics, mobile health camps providing specialist outreach to remote areas, and telemedicine services expanding access to dermatologist consultation.

SkinAI Bangladesh aims to bridge the gap for rural patients by providing instant AI-powered skin disease screening and triage, guiding patients to the appropriate level of care without the need for immediate specialist consultation.
""",
    "dghs_skin_hygiene_01.txt": """SOURCE: DGHS
TOPIC: Skin Hygiene Education — Bangladesh Primary Health Messages
---
The Directorate General of Health Services Bangladesh promotes basic skin hygiene education as a cornerstone of preventive health strategy. Skin hygiene education is integrated into school health programs, maternal and child health outreach, and community health worker activities.

Key skin hygiene messages promoted by DGHS include washing the body daily with clean water and mild soap, changing and laundering clothes regularly, not sharing personal items such as towels, combs, or razors, keeping nails clean and trimmed, treating wounds promptly to prevent infection, and wearing footwear to prevent soil-borne and fungal foot infections.

Special attention is given to hygiene in school settings, where close contact among children facilitates transmission of tinea capitis and scabies. School health programs include regular skin inspection of children, particularly for scalp lesions and scabies burrows. Teachers are trained to recognize signs of common skin conditions and refer affected children for treatment.

For families with limited access to clean water, DGHS promotes efficient hygiene practices that minimize water use. In areas with seasonal water scarcity, guidance on prioritizing hygiene practices is important.

During monsoon season, when flooding increases skin exposure to contaminated water, DGHS promotes drying skin thoroughly after water exposure and using footwear when walking through floodwater. Flood-related skin conditions including tinea pedis, folliculitis, and wound infections are common management priorities during and after flooding events.

Community hygiene education sessions conducted by community health workers address common myths about skin diseases — including that ringworm comes from worms, that scabies is caused by poor character, and that vitiligo is contagious — and replace them with accurate, evidence-based information.
""",
    "dghs_upazila_protocol_01.txt": """SOURCE: DGHS
TOPIC: DGHS Upazila Health Complex — Skin Disease Management Protocol
---
Upazila Health Complexes (UHC) are the backbone of Bangladesh's primary health care system, providing the first level of inpatient care and specialist outpatient services across the country. Each of Bangladesh's approximately five hundred upazilas has a health complex serving the rural population of that administrative unit.

For skin diseases, UHCs serve as the primary referral point from community clinics and represent the highest level of care accessible to most rural patients without significant travel burden. UHC medical officers manage the full spectrum of common skin diseases.

Standard treatment protocols at UHC level for common skin diseases include permethrin five percent cream and patient and family education for scabies; clotrimazole cream twice daily for four weeks for tinea corporis; topical corticosteroids (hydrocortisone one percent or betamethasone for severe cases) with emollients for eczema and atopic dermatitis; ketoconazole shampoo and hydrocortisone cream for seborrheic dermatitis; and appropriate wound care and antibiotic therapy for secondary bacterial skin infections.

Patients requiring systemic antifungal therapy (for tinea capitis, extensive tinea, or treatment-resistant cases), biologics for severe atopic dermatitis, or phototherapy for vitiligo and psoriasis are referred to district or medical college hospitals.

The UHC system, with appropriate training and supplies, has the capacity to manage the majority of skin disease burden in rural Bangladesh without requiring specialist referral. Ensuring consistent supply of essential dermatological medicines to all UHCs is a DGHS priority.

Digital health tools, including teledermatology and AI-assisted triage systems, represent innovative solutions to extend the reach of dermatology expertise to the UHC level and below, reducing unnecessary referrals while ensuring urgent cases reach appropriate care.
""",
    "dghs_contact_dermatitis_bd_01.txt": """SOURCE: DGHS
TOPIC: Contact Dermatitis in Bangladesh — Occupational Context
---
Contact dermatitis is an important occupational health problem in Bangladesh, particularly given the country's large agricultural and garment manufacturing workforce.

Agricultural workers represent the largest occupational group in Bangladesh, and many face significant skin exposure to chemical irritants and allergens. Pesticides, herbicides, and fertilizers applied in crop production can cause both irritant and allergic contact dermatitis. Hand and forearm involvement is most common. Farmers who work without protective gloves have the highest exposure.

Bangladesh's garment industry — one of the largest in the world — employs millions of workers who are exposed to fabric dyes, finishing chemicals, adhesives, and rubber components. Occupational contact dermatitis among garment workers is a recognized health concern. Dyes containing paraphenylenediamine and related compounds are common sensitizers.

Rickshaw pullers and other transport workers have high rates of contact dermatitis from rubber grips, sweat, and friction. Domestic workers are exposed to cleaning chemicals, detergents, and dishwashing liquid on a daily basis.

Fish processing workers and people who handle fish regularly develop fish contact dermatitis and irritant dermatitis from repeated water exposure and salt.

DGHS guidelines for occupational contact dermatitis emphasize the importance of identifying and removing the causative substance, using personal protective equipment, moisturizing regularly to maintain skin barrier function, and treating acute flares with topical corticosteroids.

Awareness among employers and workers about occupational skin disease prevention is limited. Strengthening occupational health programs in Bangladesh to address skin disease prevention in high-risk industries is a priority for DGHS occupational health policy.
""",
    "dghs_seborrheic_dermatitis_bd_01.txt": """SOURCE: DGHS
TOPIC: Seborrheic Dermatitis in Bangladesh
---
Seborrheic dermatitis is a common skin condition in Bangladesh, affecting both adults and infants. The country's hot, humid climate influences the presentation and management of the condition.

In Bangladesh, seborrheic dermatitis commonly presents as persistent dandruff, greasy flaking of the scalp, and facial redness and scaling around the nose, eyebrows, and behind the ears. The condition is often aggravated by heat and sweating during the hot summer months.

Cultural practices in Bangladesh influence both the presentation of seborrheic dermatitis and patients' treatment-seeking behavior. Frequent application of hair oils (coconut oil, mustard oil) — a widespread practice in Bangladesh — can worsen seborrheic dermatitis by providing substrate for Malassezia yeast growth and occluding the skin. Educating patients about this relationship is an important component of management.

In infants, cradle cap (seborrheic dermatitis of the scalp) is common. Bangladeshi mothers are often advised by family members or traditional practitioners to apply mustard oil or coconut oil to the scalp, which can worsen the condition. Healthcare workers should counsel mothers to use gentle, oil-free scalp care for infants with cradle cap.

Treatment options available in Bangladesh include ketoconazole two percent shampoo (available at pharmacies and UHCs), selenium sulfide shampoo, and zinc pyrithione shampoos. For facial involvement, ketoconazole cream or hydrocortisone cream provide effective treatment.

The chronic, relapsing nature of seborrheic dermatitis requires patient education about the need for ongoing maintenance treatment. Many patients in Bangladesh stop treatment when symptoms resolve, leading to frequent recurrences. Healthcare workers should explain that regular use of medicated shampoo, even when symptoms are absent, helps prevent relapse.
""",
    "dghs_general_when_to_refer_01.txt": """SOURCE: DGHS
TOPIC: When to Refer Skin Disease Patients — DGHS Guidelines
---
The Directorate General of Health Services Bangladesh provides guidance on referral criteria for skin disease patients to ensure appropriate care at the right level of the health system.

Refer to Upazila Health Complex when: the diagnosis is uncertain or the rash does not match a common pattern; the condition is not responding to initial treatment after two to three weeks; the patient is immunocompromised (HIV, diabetes, cancer); secondary bacterial infection is present and not responding to oral antibiotics; the rash is extensive or rapidly spreading; or the patient is a child with scalp ringworm (tinea capitis) requiring systemic antifungal treatment.

Refer to District Hospital when: systemic antifungal treatment is needed and not available at UHC level; the patient has a severe allergic reaction including angioedema; crusted (Norwegian) scabies is suspected; a serious bacterial skin infection (necrotizing fasciitis, extensive cellulitis) is present; there is suspicion of malignancy; or the patient has not responded to UHC-level management.

Refer to Medical College Hospital / Dermatology Specialist when: the condition requires phototherapy (vitiligo, severe psoriasis, atopic dermatitis); biologic treatment for severe atopic dermatitis or psoriasis is being considered; a complex inflammatory or bullous skin disease is suspected; occupational skin disease evaluation is needed; or patch testing for allergic contact dermatitis is required.

EMERGENCY referral to the nearest hospital IMMEDIATELY when: signs of severe sepsis or necrotizing infection are present; anaphylaxis following an allergen exposure is occurring; extensive burns with skin involvement are present; or the patient has a rapidly spreading infection with systemic signs (fever, tachycardia, confusion).

Providing a written referral letter with the clinical history, examination findings, provisional diagnosis, and treatments already given significantly improves the quality and continuity of care when patients are transferred between health system levels.
""",
    # ── CDC — TINEA (additional) ──────────────────────────────────────────────
    "cdc_tinea_06.txt": """SOURCE: CDC
TOPIC: Tinea Capitis — Scalp Ringworm in Children
---
Tinea capitis, or scalp ringworm, is a fungal infection of the scalp and hair shaft most commonly affecting school-age children between three and fourteen years. It is caused by dermatophyte fungi, primarily Trichophyton tonsurans in the United States and Trichophyton violaceum or Microsporum audouinii in other regions including parts of Asia and Africa.

The infection spreads easily in settings where children have close contact, including schools, childcare centers, and households. Sharing combs, brushes, hats, and pillows facilitates transmission. The fungus can survive on contaminated objects for extended periods.

Clinical presentation varies from mild scaling resembling dandruff to patchy hair loss with broken hair stumps. The inflammatory form, called a kerion, presents as a boggy, inflamed, tender mass from which pus can be expressed. Kerions represent an intense immune response to the fungal infection and can cause permanent scarring and alopecia if not treated promptly.

Black dot tinea capitis occurs when hair breaks off at the scalp surface, leaving dark spots visible in the pores. This pattern is associated with Trichophyton tonsurans infection.

Diagnosis requires laboratory confirmation because other conditions — including alopecia areata, seborrheic dermatitis, and psoriasis — can mimic tinea capitis. Fungal culture of scalp scrapings or broken hair remains the gold standard.

Treatment requires oral antifungal medication. Topical antifungals alone are inadequate because the infection is within the hair shaft. Griseofulvin taken with a fatty meal for six to twelve weeks is standard. Terbinafine for four weeks is an effective and shorter alternative. Antifungal shampoos can help reduce transmission.
""",
    "cdc_tinea_07.txt": """SOURCE: CDC
TOPIC: Tinea Unguium — Nail Fungal Infection
---
Tinea unguium, also known as onychomycosis, is a fungal infection of the nails caused by dermatophytes, yeasts, or non-dermatophyte molds. It is the most common nail disease, affecting approximately ten percent of the general population. Prevalence increases with age.

The toenails are affected more commonly than fingernails, partly because shoes create a warm, moist environment that favors fungal growth. Risk factors include older age, male sex, immunosuppression, peripheral vascular disease, diabetes, participation in sports, communal showers, and prior nail trauma.

Infected nails typically become thick, discolored (yellow, brown, or white), brittle, and crumbly. The nail may separate from the nail bed (onycholysis). In some cases, debris accumulates under the nail. The infection usually starts at the tip of the nail and progresses toward the base.

Diagnosis should be confirmed by laboratory testing (KOH examination, fungal culture, or PCR) before initiating treatment, because other nail conditions — including psoriasis, trauma, and lichen planus — can mimic onychomycosis. Starting long-term oral antifungal treatment without confirmed diagnosis is inappropriate.

Treatment is challenging because nails grow slowly and medications must penetrate the nail plate. Oral terbinafine for twelve weeks (toenails) is the most effective treatment, achieving cure rates of approximately seventy-five percent. Itraconazole pulse therapy is an alternative. Topical treatments alone are generally effective only for very early, limited infections.

In Bangladesh and other tropical countries, tinea unguium is common, particularly among agricultural workers and people who frequently walk barefoot.
""",
    "cdc_tinea_08.txt": """SOURCE: CDC
TOPIC: Tinea Cruris — Jock Itch
---
Tinea cruris, commonly known as jock itch, is a dermatophyte infection of the groin, inner thighs, and buttocks. It is one of the most common fungal infections in adults and is significantly more prevalent in males than females. It frequently coexists with tinea pedis (athlete's foot) and tinea unguium.

The condition is particularly common in tropical and subtropical regions including Bangladesh, where heat, humidity, and sweating create conditions that favor fungal growth in the groin area. Wearing tight-fitting synthetic clothing that traps moisture worsens the condition.

Tinea cruris presents as a red, itchy rash with a well-defined, raised border in the groin area. The rash often has a ring-like appearance, with the active border at the periphery and some central clearing. The scrotum is usually spared, which helps distinguish tinea cruris from candidal intertrigo, in which the scrotum is typically involved.

Risk factors include excessive sweating, obesity, wearing tight clothing, communal showering, and contact with infected individuals or contaminated items. Athletes, military personnel, and workers in hot environments are particularly susceptible.

Treatment with topical antifungal cream (clotrimazole, miconazole, or terbinafine) applied twice daily for two to four weeks is effective for most cases. The groin area should be kept clean and dry. Loose-fitting, breathable cotton underwear is recommended. Antifungal powder can be applied to maintain dryness after treatment.

Recurrence is common if underlying predisposing factors are not addressed. Concurrent treatment of tinea pedis and tinea unguium, if present, reduces recurrence risk.
""",

    # ── CDC — SCABIES (additional) ────────────────────────────────────────────
    "cdc_scabies_06.txt": """SOURCE: CDC
TOPIC: Scabies in Elderly and Institutional Settings
---
Scabies in nursing homes, long-term care facilities, and hospitals poses particular challenges because transmission can occur rapidly among residents and staff, and because elderly or debilitated residents may develop crusted (Norwegian) scabies with atypical presentations.

Elderly individuals may have reduced ability to scratch, muted immune responses, or cognitive impairment that prevents them from communicating symptoms, leading to delays in diagnosis. In elderly patients, scabies may present with diffuse pruritus and non-specific rash rather than the classic burrows and distribution seen in younger adults.

When one resident in a care facility is diagnosed with scabies, a thorough investigation of all residents and staff who have had direct skin contact with the case is essential. Outbreak management requires simultaneous treatment of all affected individuals, their close contacts, and all staff.

Scabies outbreaks in institutional settings can persist for months if not managed aggressively. A single case of crusted scabies in a care facility can infect dozens of residents and staff due to the vast numbers of mites present and the shedding of infected skin scales.

Management of institutional outbreaks requires coordination between clinical staff, administration, infection control teams, and public health authorities. Key elements include rapid case identification, simultaneous treatment of all cases and contacts, environmental decontamination (laundering all bedding and clothing in hot water), and follow-up assessment at two weeks.

Staff should use appropriate personal protective equipment — gloves and gowns — when caring for patients with known or suspected scabies. Hand hygiene before and after patient contact is essential.

Prevention of future outbreaks requires education of all staff about scabies recognition, prompt reporting of suspected cases, and review of infection control protocols.
""",

    # ── CDC — ATOPIC DERMATITIS (additional) ──────────────────────────────────
    "cdc_atopic_dermatitis_04.txt": """SOURCE: CDC
TOPIC: Atopic Dermatitis Diagnosis and Comorbidities
---
The diagnosis of atopic dermatitis is based on clinical criteria rather than specific laboratory tests. The classic criteria require the presence of itching, typical distribution and morphology of rash, and chronic or relapsing course. No single finding is pathognomonic.

Diagnostic criteria commonly used include the Hanifin-Rajka criteria and the UK Working Party criteria. Both require the presence of pruritus and at least three of the following: history of skin crease involvement, history of asthma or hay fever, history of dry skin, visible flexural eczema, and onset before two years of age.

Allergy testing — both skin prick testing and specific IgE blood tests — can identify sensitizations that may be relevant to eczema management, particularly in patients with moderate to severe disease or suspected food triggers. However, a positive allergy test does not necessarily mean the allergen is causing atopic dermatitis flares; clinical relevance must be assessed in the context of the patient's history.

Atopic dermatitis is strongly associated with other atopic conditions. Approximately thirty percent of patients have asthma, and up to sixty percent have allergic rhinitis. The sequence in which these conditions develop — eczema in infancy, food allergy, asthma, allergic rhinitis — is often called the atopic march.

Psychological comorbidities are common and often underrecognized. Depression and anxiety occur at approximately double the rate in people with atopic dermatitis compared to the general population. Attention-deficit hyperactivity disorder (ADHD) is more prevalent in children with atopic dermatitis. These comorbidities should be assessed and managed as part of comprehensive care.

Infections are important comorbidities. Eczema herpeticum — a serious widespread herpes simplex infection — requires urgent antiviral treatment and can be life-threatening.
""",
    "cdc_atopic_dermatitis_05.txt": """SOURCE: CDC
TOPIC: Atopic Dermatitis and Climate — Impact on Bangladesh Patients
---
Climate plays a significant role in atopic dermatitis severity. In tropical countries including Bangladesh, the climate interacts with atopic dermatitis in complex ways that differ from temperate country patterns.

In Bangladesh, the hot, humid summers typically worsen atopic dermatitis through increased sweating. Sweat contains proteins and salts that irritate sensitive, barrier-impaired skin and trigger intense itching. Sweating under occlusive clothing traps moisture against the skin, worsening maceration and irritation.

Conversely, the cooler, drier winter months in Bangladesh bring their own challenges. Lower humidity and cooler temperatures promote evaporation of water from skin, worsening dryness. Patients with atopic dermatitis may experience increased skin cracking and fissuring during winter.

The monsoon season transition — when temperature and humidity change rapidly — is associated with increased eczema flares in many Bangladeshi patients.

Air pollution is worsening in Bangladesh's cities, particularly Dhaka. Particulate matter and chemical pollutants can penetrate impaired skin barrier and trigger inflammation, contributing to the rising incidence of atopic dermatitis in urban Bangladesh.

Practical adaptations for Bangladeshi patients include taking cool (not cold) baths rather than hot showers, applying moisturizer within minutes of bathing to counteract the drying effects of water evaporation, wearing loose, cotton clothing that allows air circulation, using fans to reduce sweating, and seeking shade during the hottest parts of the day.

Mosquito bites in Bangladesh can trigger intense reactions and Koebner-like responses in atopic skin, further complicating management during mosquito season.
""",

    # ── CDC — CONTACT DERMATITIS (additional) ────────────────────────────────
    "cdc_contact_dermatitis_03.txt": """SOURCE: CDC
TOPIC: Hand Dermatitis and Occupational Contact Dermatitis
---
Hand dermatitis is one of the most common occupational skin diseases, affecting between two and ten percent of the general population and even higher proportions in certain occupational groups. The hands are the most frequent site of contact dermatitis because they are the primary points of contact with workplace substances.

Occupations with highest rates of hand dermatitis include healthcare workers (frequent hand washing and glove use), food handlers (wet work, food juices, and cleaning chemicals), hairdressers (shampoos, dyes, bleach, and permanents), construction workers (cement, solvents, and epoxy resins), domestic cleaners (detergents and bleach), and agricultural workers (pesticides, fertilizers, and plant materials).

Wet work — defined as having the hands immersed in liquids for more than two hours per day, wearing waterproof gloves for an equivalent period, or washing hands more than twenty times per day — is the most important occupational risk factor for hand dermatitis. Prolonged wet work damages the stratum corneum and impairs skin barrier function.

Prevention of occupational hand dermatitis requires a hierarchy of controls. The most effective approach is eliminating or substituting the causative substance. If elimination is not possible, engineering controls (ventilation, automation), administrative controls (reducing exposure time, rotating workers), and finally personal protective equipment (gloves, barrier creams) should be implemented.

When gloves are used, appropriate selection is essential. Latex gloves cause allergic contact dermatitis in sensitized individuals. Nitrile or vinyl gloves are safer alternatives. Wearing gloves also creates an occlusive environment that can worsen irritant dermatitis. Wearing cotton liner gloves inside rubber gloves can reduce skin maceration.

Treatment of established hand dermatitis combines avoidance of triggers, regular moisturizer application, and topical corticosteroids for flares.
""",

    # ── CDC — VITILIGO (additional) ───────────────────────────────────────────
    "cdc_vitiligo_03.txt": """SOURCE: CDC
TOPIC: Vitiligo — Associated Medical Conditions
---
Vitiligo is associated with several other autoimmune and immune-mediated conditions. Screening for these conditions at the time of vitiligo diagnosis is recommended, as early detection improves outcomes.

Thyroid disease is the most commonly associated condition. Hashimoto's thyroiditis (autoimmune hypothyroidism) and Graves' disease (autoimmune hyperthyroidism) occur at significantly higher rates in people with vitiligo than in the general population. Thyroid antibodies (anti-TPO and anti-thyroglobulin) are present in twenty to thirty percent of vitiligo patients. All vitiligo patients should have thyroid function tests at diagnosis and periodically thereafter.

Type 1 diabetes mellitus is associated with vitiligo, reflecting shared autoimmune mechanisms. People with vitiligo should be aware of symptoms of diabetes.

Alopecia areata — autoimmune hair loss — co-occurs with vitiligo more often than expected by chance. Both conditions involve T cell-mediated attack on specific cell types.

Pernicious anemia, an autoimmune condition causing vitamin B12 deficiency, is associated with vitiligo. Vitamin B12 deficiency can cause neurological complications if untreated.

Addison's disease (autoimmune adrenal insufficiency) and primary hypogonadism are rarer associated conditions.

Inflammatory bowel disease, rheumatoid arthritis, and psoriasis have also been reported in association with vitiligo, though the relationships are less strong.

Halo nevi — nevi (moles) surrounded by a ring of depigmentation — are associated with vitiligo and may precede its development.

People with vitiligo and their families should be educated about the signs of these associated conditions so they can seek appropriate evaluation promptly.
""",

    # ── NIH — TINEA (additional) ──────────────────────────────────────────────
    "nih_tinea_04.txt": """SOURCE: NIH
TOPIC: Tinea Pedis — Athlete's Foot
---
Tinea pedis is the most common superficial fungal infection worldwide, affecting up to twenty-five percent of adults at some point in their lives. It occurs when dermatophyte fungi infect the skin of the foot, particularly the toe web spaces, the sole, and the sides of the foot.

The condition presents in several clinical patterns. The interdigital form, most common, affects the skin between toes — particularly between the fourth and fifth toes. The skin appears macerated, white, and scaly, often with fissuring. The vesicular form causes small, intensely itchy blisters on the sole and instep. The moccasin form causes chronic, diffuse scaling and thickening of the sole with a dry, powdery appearance.

Transmission occurs in environments where bare skin contacts contaminated surfaces. Public swimming pools, showers, locker rooms, and communal bathing areas are high-risk settings. The fungi survive in moist environments and adhere to desquamated skin cells.

Predisposing factors include wearing occlusive footwear that maintains heat and moisture, excessive sweating of the feet, immunosuppression, and peripheral vascular disease. In Bangladesh, working in flooded paddy fields while wearing rubber boots creates ideal conditions for tinea pedis.

Tinea pedis often coexists with tinea unguium (nail infection) and tinea cruris. Treating tinea pedis may reduce recurrence of tinea cruris by eliminating a reservoir of infection.

Topical antifungal creams applied to the affected areas and between all toe spaces once or twice daily for two to four weeks are effective. Keeping feet clean and dry, using antifungal powder in shoes, wearing absorbent socks, and using footwear in communal areas prevent infection and recurrence.
""",
    "nih_tinea_05.txt": """SOURCE: NIH
TOPIC: Tinea Versicolor — Pityriasis Versicolor
---
Tinea versicolor, now more precisely called pityriasis versicolor, is a superficial fungal infection caused by Malassezia species — lipophilic yeasts that are part of normal skin flora. Despite the name containing tinea, it is not caused by dermatophytes. The condition is characterized by multiple small, discrete hypopigmented or hyperpigmented patches on the trunk and proximal limbs.

The patches appear lighter than the surrounding skin in people with tanned or darker skin tones — a common finding in tropical countries including Bangladesh — because Malassezia produces azelaic acid, which inhibits melanin transfer to keratinocytes. In fair-skinned individuals or after sun exposure, the patches may appear darker than surrounding skin.

Pityriasis versicolor is extremely common in tropical countries due to the high ambient temperature and humidity that promote Malassezia overgrowth. Studies from Bangladesh suggest prevalence rates of five to ten percent in the general population.

The condition commonly affects the trunk, upper arms, neck, and abdomen. The face is less commonly involved. Mild itching may be present, but many patients have no symptoms and seek medical care primarily for cosmetic reasons.

Diagnosis is typically clinical, supported by a positive KOH examination showing the characteristic short hyphae and round spores in a pattern described as spaghetti and meatballs. Wood's lamp examination causes some affected skin to fluoresce yellow-green.

Treatment with topical antifungal agents — selenium sulfide, ketoconazole shampoo, or zinc pyrithione — applied to affected areas for two to four weeks is effective. Recurrence is common, and monthly prophylactic application may be needed in predisposed individuals. Skin color normalization after treatment takes months as melanocytes recover.
""",

    # ── NIH — SCABIES (additional) ────────────────────────────────────────────
    "nih_scabies_03.txt": """SOURCE: NIH
TOPIC: Scabies Complications and Secondary Infections
---
While scabies itself is treatable, its complications — particularly secondary bacterial infections — are responsible for much of its associated morbidity, especially in tropical settings.

Scratching the intensely itchy scabies rash breaks the skin surface, creating entry points for bacteria. Secondary bacterial superinfection with Staphylococcus aureus and Streptococcus pyogenes (Group A Streptococcus) is the most common complication of scabies.

Staphylococcal superinfection manifests as impetiginized lesions with honey-colored crusting, folliculitis, or more severe infections including cellulitis and furunculosis. Streptococcal infection appears similarly but may have a more violaceous hue.

In tropical countries including Bangladesh, scabies-associated streptococcal skin infections are a significant cause of post-streptococcal glomerulonephritis (PSGN) — a kidney inflammation that can cause acute renal failure. This is particularly concerning in children. The contribution of scabies to PSGN burden in Bangladesh is underappreciated.

Scabies-associated streptococcal infections may also contribute to acute rheumatic fever in endemic regions, though this relationship is less well-established than for pharyngeal streptococcal infection.

Management of complicated scabies requires simultaneous treatment of the scabies infestation and the bacterial superinfection. Systemic antibiotics (typically flucloxacillin for staphylococcal infections, or amoxicillin/phenoxymethylpenicillin for streptococcal infections) are required for cellulitis and more extensive bacterial infections. Topical antibiotics may suffice for localized impetigo.

Recognition that scabies complications extend beyond skin discomfort to systemic disease is essential for appropriate public health prioritization in Bangladesh and similar settings.
""",

    # ── NIH — ATOPIC DERMATITIS (additional) ──────────────────────────────────
    "nih_atopic_dermatitis_02.txt": """SOURCE: NIH
TOPIC: Atopic Dermatitis — Triggers and Flare Management
---
Understanding and managing triggers is central to long-term atopic dermatitis control. Triggers are factors that cause the immune system to activate and worsen skin inflammation in predisposed individuals. Triggers vary between individuals and must be identified through careful observation.

Skin irritants are among the most common triggers. These include soaps and cleansers that disrupt the skin barrier, detergents, bleach, chlorine in swimming pools, some cosmetics and fragrances, rough fabrics (particularly wool and synthetic fibers), adhesives, and cigarette smoke. Environmental irritants in Bangladesh include dust, smoke from cooking fires (particularly in rural areas where biomass fuel is used), and industrial pollutants.

Allergens can trigger atopic dermatitis through various mechanisms. House dust mites are the most clinically relevant inhalant allergen. Pet dander from cats and dogs is another common sensitizer. Pollen, mold spores, and cockroach allergens are relevant in different settings. Food allergens, particularly milk, eggs, wheat, soy, and peanuts, are relevant triggers in infants and young children.

Infectious agents frequently trigger atopic dermatitis flares. Staphylococcus aureus colonizes affected skin and produces toxins that act as superantigens and stimulate inflammation. Antistaphylococcal treatment can improve atopic dermatitis in colonized patients. Herpes simplex virus can cause a severe flare called eczema herpeticum.

Psychological stress is a well-recognized trigger that worsens atopic dermatitis through neuroimmune mechanisms. Stress management and mental health support are components of comprehensive care.

Flare management involves increasing topical anti-inflammatory treatment, addressing any infection, and identifying and removing the triggering factor. A written action plan helps patients respond appropriately to changing disease severity.
""",
    "nih_atopic_dermatitis_03.txt": """SOURCE: NIH
TOPIC: Atopic Dermatitis in Infants — Recognition and Care
---
Atopic dermatitis commonly begins in infancy, with the first signs often appearing between two and six months of age. Recognizing and managing infantile eczema early can reduce disease severity and prevent skin barrier deterioration.

In young infants, the rash typically appears on the cheeks, forehead, and scalp. It has a red, weeping, and crusting appearance. The diaper area is usually spared, possibly because the moist environment of diapers maintains skin hydration. As infants begin to crawl, the knees and shins may become affected from friction against surfaces.

Intense itching in infants manifests as rubbing the face and head against bedding, fussiness, disrupted sleep, and failure to thrive in severe cases. The infant cannot scratch in the coordinated way that older children do, but rubbing causes similar skin damage.

Parents are often distressed by the appearance of the rash and the infant's discomfort. Education and emotional support for parents are important components of care. Parents need to understand that eczema is not caused by anything they did wrong and is not contagious.

Emollient (moisturizer) therapy is the cornerstone of infant eczema management. Thick, fragrance-free creams or ointments should be applied generously after every bath. Some studies suggest that daily emollient application from birth may reduce the risk of developing atopic dermatitis in high-risk infants.

Topical hydrocortisone 0.5% or 1% cream or ointment is safe and effective for treating flares in infants. It should be used in the lowest effective amount for the shortest necessary time, with guidance from a healthcare provider.

Breastfeeding is encouraged for atopic families, though the evidence for its protective effect is moderate.
""",

    # ── NIH — ECZEMA (additional) ─────────────────────────────────────────────
    "nih_eczema_02.txt": """SOURCE: NIH
TOPIC: Dyshidrotic Eczema and Nummular Eczema
---
Dyshidrotic eczema (pompholyx) is a distinct form of eczema characterized by small, intensely itchy blisters (vesicles) on the edges of the fingers, toes, palms, and soles. The blisters are typically deep-seated, giving them a tapioca-like appearance. They can coalesce to form larger blisters.

The blisters cause significant discomfort, burning, and itching. After the blisters resolve over two to three weeks, the skin may become dry, red, and cracked. Recurrent episodes are characteristic.

The exact cause of dyshidrotic eczema is not fully understood. Triggers include emotional stress, sweating, seasonal allergens (it often peaks in spring and summer), and sensitization to nickel or cobalt. Contact with certain detergents or metals can trigger episodes.

Treatment of dyshidrotic eczema during the acute phase involves cool, moist compresses to reduce blistering and itch, followed by potent topical corticosteroids once the blisters begin to resolve. For severe or recurrent cases, phototherapy or systemic agents may be required.

Nummular eczema (nummular dermatitis) presents as coin-shaped, itchy, inflamed patches of skin. The patches are often intensely pruritic and can weep fluid in the acute phase. The distribution typically involves the limbs and trunk rather than the typical flexural sites of atopic dermatitis.

Nummular eczema is triggered by dry skin, minor skin injuries, insect bites, and certain medications. It is more common in middle-aged and older adults.

Both dyshidrotic eczema and nummular eczema are managed with topical corticosteroids, regular emollient use, and identification and avoidance of triggers. Secondary bacterial infections are treated with appropriate antibiotics.
""",
    "nih_eczema_03.txt": """SOURCE: NIH
TOPIC: Eczema and Infection Risk
---
Eczema significantly increases susceptibility to skin infections due to the compromised skin barrier and immune dysregulation associated with the condition. Both bacterial and viral infections complicate eczema and can trigger severe flares.

Staphylococcus aureus colonizes the skin of more than ninety percent of people with moderate to severe atopic dermatitis, compared to approximately thirty percent of the general population. Staphylococcal colonization contributes to eczema inflammation through the production of toxins that act as superantigens and stimulate immune cells. Periods of increased colonization often precede or accompany flares.

Signs of secondary bacterial infection requiring treatment include honey-colored crusting (impetigo), increased redness and warmth, pustules, swollen lymph nodes, and systemic signs like fever. When infection is suspected, topical or oral antibiotics (typically targeting Staphylococcus aureus) are required.

Eczema herpeticum is a potentially life-threatening infection caused by herpes simplex virus (HSV) spreading across eczematous skin. It presents as clusters of punched-out erosions, often with fever and malaise. Immediate antiviral treatment with acyclovir or valacyclovir is required. Eczema herpeticum is a dermatological emergency.

Molluscum contagiosum, a viral skin infection that usually causes mild, localized disease in immunocompetent individuals, can spread extensively in children with atopic dermatitis.

Fungal infections, particularly dermatophyte infections (tinea), can also complicate atopic dermatitis and may be confused with eczema flares.

Reducing Staphylococcal colonization through dilute bleach baths (0.005% sodium hypochlorite, one teaspoon per gallon of water) twice weekly can reduce infection frequency and improve eczema control. This should be done under healthcare provider guidance.
""",

    # ── NIH — CONTACT DERMATITIS (additional) ────────────────────────────────
    "nih_contact_dermatitis_02.txt": """SOURCE: NIH
TOPIC: Allergic Contact Dermatitis — Common Allergens
---
Allergic contact dermatitis results from a delayed-type hypersensitivity reaction to specific allergens. Sensitization requires at least one prior exposure. Subsequent exposures trigger a reaction within twelve to seventy-two hours at the site of contact.

Nickel is the most common contact allergen worldwide. It is found in jewelry (earrings, necklaces, belt buckles, watchbands), clothing fasteners, coins, and many everyday objects. Ear piercing is a major route of nickel sensitization. In Bangladesh, nickel sensitization from cheap metal jewelry and clothing fasteners is common.

Fragrances represent a major category of skin allergens. Hundreds of chemical compounds contribute to fragrance mixtures. Common sensitizers include geraniol, eugenol, cinnamic aldehyde, and isoeugenol. Fragrances are present in perfumes, colognes, deodorants, soaps, shampoos, and cosmetics.

Preservatives used in cosmetics and personal care products are an increasing cause of contact allergy. Methylisothiazolinone (MI) and methylchloroisothiazolinone (MCI) are found in many rinse-off and leave-on products. Formaldehyde releasers (quaternium-15, DMDM hydantoin) and parabens are other preservative allergens.

Hair dyes containing paraphenylenediamine (PPD) are a common sensitizer. Hair dye allergy can cause severe reactions involving the scalp, forehead, neck, and eyelids. Henna tattoos often contain PPD and can cause sensitization that persists with subsequent exposures.

Rubber chemicals in gloves, footwear, and elastic bands are important occupational allergens. Latex allergen itself causes immediate-type reactions in some individuals.

Topical medications including neomycin, bacitracin, and topical anesthetics are common sensitizers, particularly in patients who use them frequently for wound care.
""",
    "nih_contact_dermatitis_03.txt": """SOURCE: NIH
TOPIC: Contact Dermatitis Treatment and Long-term Management
---
Effective management of contact dermatitis requires both treating the acute reaction and identifying the causative substance to prevent recurrence.

In the acute phase, removing the offending substance is the first priority. Wash the affected area thoroughly with mild soap and water. Apply cool, wet compresses to relieve itch and reduce weeping. Avoid further exposure to the suspected substance during evaluation.

Topical corticosteroids are the primary treatment for reducing inflammation. For localized reactions on the body, a medium-potency corticosteroid (such as triamcinolone acetonide 0.1% cream) applied twice daily for one to two weeks is appropriate. For facial or genital involvement, a low-potency agent (hydrocortisone 1%) is preferred. For severe reactions covering large body surface areas, a short course of oral corticosteroids (prednisone) may be required.

Antihistamines provide some relief from itching. Oral antihistamines are particularly helpful for nighttime itching.

Secondary bacterial infections require topical or systemic antibiotics depending on severity.

After the acute reaction resolves, patch testing by a dermatologist is the definitive investigation for allergic contact dermatitis. Patch testing identifies specific allergens from a standardized panel. Results guide avoidance counseling.

Long-term management is centered on avoiding the identified allergen. Allergen avoidance information should include all sources of the allergen in products, materials, and workplace substances. Safe alternatives should be provided.

Regular moisturizer use to maintain skin barrier function is important for long-term management, particularly for hand dermatitis.

In occupational contact dermatitis, workplace assessment and modification are essential components of management alongside individual treatment.
""",

    # ── NIH — SEBORRHEIC DERMATITIS (additional) ──────────────────────────────
    "nih_seborrheic_dermatitis_02.txt": """SOURCE: NIH
TOPIC: Seborrheic Dermatitis — Cradle Cap in Infants
---
Cradle cap is the common term for seborrheic dermatitis affecting the scalp of infants. It typically appears within the first weeks to months of life and usually resolves spontaneously by twelve months of age.

Cradle cap appears as greasy, yellow or brownish, scaly patches on the infant's scalp. The scales may be thick and adherent. Unlike adult seborrheic dermatitis, cradle cap is generally not itchy and does not cause discomfort to the infant.

The cause of cradle cap relates to stimulation of sebaceous glands by maternal hormones transferred before birth. These hormones cause overproduction of sebum in the infant's skin. Malassezia yeast, which colonizes sebum-rich skin, may contribute to the scaling.

Cradle cap can extend to the eyebrows, eyelids, and diaper area. When it spreads beyond the scalp, it may be confused with other conditions including atopic dermatitis. Unlike atopic dermatitis, cradle cap typically does not cause intense itching.

In most infants, cradle cap resolves without treatment. Gentle washing with a soft brush or comb to loosen scales after softening them with baby oil or petroleum jelly is helpful. Apply the oil, leave for a few minutes, then gently comb out the scales before shampooing.

If scales are extensive or spreading, a ketoconazole two percent shampoo or a mild hydrocortisone cream may be used under the guidance of a healthcare provider.

Parents should be reassured that cradle cap is common, benign, and typically temporary. It is not caused by poor hygiene or anything the parent did wrong.
""",
    "nih_seborrheic_dermatitis_03.txt": """SOURCE: NIH
TOPIC: Seborrheic Dermatitis — Diagnosis and Differential
---
The diagnosis of seborrheic dermatitis is clinical, based on the characteristic distribution of greasy scales on erythematous skin in sebum-rich areas. No laboratory tests or biopsies are routinely needed.

The scalp is most commonly affected, presenting with adherent white or yellowish scales (dandruff) on an erythematous base. The scale may be greasy or dry. Pruritus varies from absent to severe. The condition can extend to the hairline, forehead, ears (including the ear canal), and nape of the neck.

Facial seborrheic dermatitis affects the nasolabial folds, eyebrows, glabella, and eyelid margins. The affected skin appears red and slightly scaly. Blepharitis (scaling and redness of the eyelid margins) is a common manifestation.

The differential diagnosis of seborrheic dermatitis includes psoriasis (which can be indistinguishable on the scalp — termed sebopsoriasis when features overlap), atopic dermatitis (usually more pruritic, different distribution), contact dermatitis (related to specific exposures), rosacea (on the face, without scaling), and tinea capitis (children, hair loss, confirmed by culture).

In immunocompromised patients, particularly those with HIV infection, seborrheic dermatitis can be severe and widespread, affecting atypical areas. Severe seborrheic dermatitis may be the presenting sign of HIV infection.

Dandruff — mild scalp seborrheic dermatitis without inflammation — is effectively managed with regular use of over-the-counter medicated shampoos. When inflammation is present, prescription antifungal or anti-inflammatory treatments are required.

Most patients benefit from long-term maintenance treatment with medicated shampoo even during remission periods to prevent recurrence.
""",

    # ── NIH — VITILIGO (additional) ───────────────────────────────────────────
    "nih_vitiligo_03.txt": """SOURCE: NIH
TOPIC: Vitiligo — Treatment Options
---
The management of vitiligo aims to halt progression, repigment affected areas, and address psychological impact. Treatment selection depends on the extent and type of vitiligo, skin type, patient age, and treatment availability.

Topical treatments are appropriate for limited vitiligo. Topical corticosteroids are widely used as first-line therapy, particularly for localized vitiligo in early stages. Repigmentation, when it occurs, typically appears around hair follicles as small brown spots that gradually coalesce. Medium-potency corticosteroids are used on the body; low-potency on the face.

Topical calcineurin inhibitors (tacrolimus 0.1% ointment or pimecrolimus 1% cream) are preferred alternatives for the face and neck, as they do not cause skin atrophy. They are particularly effective for facial vitiligo and are safe for long-term use.

Narrowband UVB (NB-UVB) phototherapy is the most widely used and effective treatment for widespread vitiligo. It involves exposing skin to specific ultraviolet B wavelengths two to three times weekly for six months to two years. Repigmentation responses of fifty percent or more are common with adequate treatment duration.

Excimer laser delivers targeted 308-nm UVB light to specific patches and is useful for focal or localized vitiligo.

Surgical options are appropriate for stable vitiligo that has not responded to other treatments. Melanocyte-keratinocyte transplantation procedure (MKTP) and split-thickness skin grafting can achieve repigmentation in carefully selected patients.

Ruxolitinib cream, a JAK1/JAK2 inhibitor, has FDA approval for non-segmental vitiligo and represents an important advance. It reduces the autoimmune attack on melanocytes and allows repigmentation.

Combination therapy — for example, NB-UVB with topical tacrolimus — may enhance repigmentation compared to either treatment alone.
""",
    "nih_vitiligo_04.txt": """SOURCE: NIH
TOPIC: Vitiligo — Diagnosis and Assessment
---
The diagnosis of vitiligo is clinical in the vast majority of cases, based on the characteristic appearance of well-demarcated, depigmented white patches. In individuals with darker skin tones — as in Bangladesh — the contrast between depigmented and surrounding skin is striking and diagnosis is usually straightforward.

Wood's lamp (ultraviolet A light) examination enhances the contrast between depigmented and normally pigmented skin, particularly in fair-skinned individuals where the patches may not be easily visible under normal light. Under Wood's lamp, vitiligo patches fluoresce bright white due to the absence of melanin.

The differential diagnosis of vitiligo includes pityriasis versicolor (tinea versicolor — hypopigmented rather than depigmented, with fine scale, positive KOH examination), pityriasis alba (poorly demarcated, hypopigmented patches common in children with atopic tendency), post-inflammatory hypopigmentation (follows skin inflammation, less sharp border), chemical leukoderma (history of chemical exposure, usually occupational), leprosy (associated with reduced sensation in the patch, confirmed by skin biopsy), and nevus depigmentosus (present from birth, stable, irregular border).

Distinguishing vitiligo from leprosy is particularly important in Bangladesh and other South Asian countries, where leprosy remains present (though declining) and carries profound social stigma. In leprosy, depigmented or hypopigmented patches are associated with reduced sensation. The Fite-stained biopsy and skin-slit smear for acid-fast bacilli confirm leprosy.

Dermoscopy can identify residual melanocytes at follicular openings, which is a positive prognostic sign for repigmentation response to treatment.

Thyroid function testing and a complete blood count are the minimum baseline investigations for newly diagnosed vitiligo.
""",

    # ── WHO — ADDITIONAL ─────────────────────────────────────────────────────
    "who_scabies_03.txt": """SOURCE: WHO
TOPIC: WHO NTD Roadmap 2021–2030 — Scabies Targets
---
The World Health Organization's 2021–2030 Roadmap for Neglected Tropical Diseases sets specific targets for scabies control that are relevant for Bangladesh and other endemic countries.

The WHO NTD Roadmap identifies scabies as a target for intensified control, with the goal of ensuring access to care for all affected people and reducing the burden of disease and its complications by 2030.

Key strategic approaches outlined by WHO for scabies control include: preventive chemotherapy through mass drug administration (MDA) with ivermectin in communities with prevalence above ten percent; case management to ensure all diagnosed individuals and their contacts receive prompt treatment; surveillance systems to monitor disease burden and treatment effectiveness; and community health education.

WHO estimates that with sustained implementation of these strategies, scabies prevalence in highly endemic communities can be reduced by more than seventy percent by 2030.

The integration of scabies control into existing NTD programs — particularly those already distributing ivermectin for lymphatic filariasis or river blindness — offers opportunities for cost-effective co-administration.

For Bangladesh, where scabies is endemic but prevalence surveys are limited, improving epidemiological data through systematic surveys is a priority. This evidence base is needed to target MDA programs appropriately and to monitor progress.

Bangladesh's existing community health worker network — including health assistants and community health assistants who conduct regular household visits — provides a platform for scabies case finding, treatment delivery, and community education that can be leveraged for scabies control without building new systems.
""",
    "who_tinea_02.txt": """SOURCE: WHO
TOPIC: WHO Essential Medicines for Skin Diseases
---
The World Health Organization's Essential Medicines List (EML) includes several medications critical for managing common skin diseases. Access to these medicines in primary healthcare settings is fundamental to reducing the burden of skin disease in low- and middle-income countries.

For fungal skin infections (tinea, pityriasis versicolor), the WHO EML includes clotrimazole 1% cream for topical treatment, and griseofulvin oral tablets for systemic treatment of tinea capitis and extensive tinea. Fluconazole is listed for systemic fungal infections. Ketoconazole shampoo is included for seborrheic dermatitis.

For scabies, the WHO EML includes permethrin 5% cream as the preferred topical scabicide, and ivermectin oral tablets as the systemic option, particularly for outbreaks and mass drug administration.

For inflammatory skin conditions, hydrocortisone 1% cream (low-potency corticosteroid) and betamethasone cream (medium/high-potency) are listed for eczema and atopic dermatitis management.

For secondary bacterial skin infections, phenoxymethylpenicillin and amoxicillin are included for streptococcal infections, and cloxacillin or dicloxacillin for staphylococcal infections.

Ensuring these medicines are consistently available at all levels of the health system — from community clinics through district hospitals — is a WHO advocacy priority. Stock-outs and supply chain disruptions disproportionately affect rural populations who have fewer alternative sources.

In Bangladesh, the DGHS supply chain distributes WHO essential medicines to upazila health complexes and community clinics. Monitoring and improving supply chain reliability is essential for effective skin disease management at the primary care level.
""",
    "who_eczema_01.txt": """SOURCE: WHO
TOPIC: WHO Perspective — Eczema and Non-communicable Skin Diseases
---
Atopic dermatitis and eczema are classified as non-communicable diseases (NCDs) by the World Health Organization. The WHO NCD framework increasingly recognizes the burden of chronic inflammatory skin conditions alongside the more commonly tracked NCDs such as cardiovascular disease, diabetes, cancer, and chronic respiratory conditions.

The global burden of atopic dermatitis is estimated at two hundred thirty million affected individuals, with the highest burden in children. In low- and middle-income countries, the prevalence is rising as these countries undergo epidemiological transition associated with urbanization and lifestyle changes.

WHO recognizes that chronic skin diseases including atopic dermatitis are associated with significant mental health burden. Internationally, there is growing recognition that skin conditions should be addressed as part of comprehensive NCD programs rather than exclusively as dermatological conditions.

Access to affordable topical corticosteroids — the cornerstone of atopic dermatitis treatment — is highly variable globally. In many low- and middle-income countries, patients rely on potent corticosteroids obtained without prescription, leading to side effects from inappropriate use. Generic low- and medium-potency corticosteroids are on the WHO Essential Medicines List.

Emollients (moisturizers) are not currently on the WHO EML, despite being the cornerstone of daily eczema management. This represents a gap in access for patients in resource-limited settings.

WHO supports community-based approaches to eczema management that include patient education, support groups, and integration of skin disease care into primary health care. Training community health workers to recognize and manage common inflammatory skin conditions is endorsed as a strategy for expanding access to care.
""",
    "who_bangladesh_skin_01.txt": """SOURCE: WHO
TOPIC: WHO Country Support — Bangladesh Skin Disease Burden
---
Bangladesh is classified as a lower-middle-income country by the World Bank, with a population of approximately one hundred seventy million people. The country faces a substantial burden of both communicable and non-communicable skin diseases, with significant unmet needs for dermatological care.

WHO's country office in Bangladesh works with the Government of Bangladesh and the Directorate General of Health Services to strengthen skin disease management within the national health system. Priority areas include neglected tropical diseases (particularly scabies and leprosy), improving access to essential dermatological medicines, and training healthcare workers in basic dermatology.

The dermatologist-to-population ratio in Bangladesh is among the lowest in the region, estimated at approximately one per two hundred fifty thousand people. Most dermatologists practice in major urban centers, leaving vast rural populations with extremely limited access to specialist care.

Bangladesh's geographical characteristics create specific skin disease challenges. The low-lying delta geography is prone to flooding during monsoon season, which increases exposure to skin infections and wounds. The subtropical climate with high humidity promotes fungal infections.

WHO supports telemedicine and digital health innovations as strategies to extend dermatological expertise to remote areas. AI-assisted skin disease screening tools represent a promising approach to improving access to quality care for rural populations.

WHO's Bangladesh country programs include integration of skin disease management into maternal and child health services, school health programs, and primary care training curricula. The WHO-SEARO regional office provides technical support to Bangladesh's national skin disease programs.
""",
    "who_climate_skin_01.txt": """SOURCE: WHO
TOPIC: Climate Change and Skin Diseases
---
The World Health Organization recognizes climate change as a growing threat to human health, with skin diseases among the conditions expected to be affected by changing environmental conditions.

Rising temperatures and increased humidity associated with climate change are expected to expand the geographic range of many fungal and parasitic skin diseases. Dermatophyte infections (tinea) and scabies thrive in warm, moist conditions. As global temperatures rise, the zones of high endemic prevalence for these conditions are expected to shift.

Increased frequency and intensity of extreme weather events — flooding, heat waves, and droughts — affect skin health in distinct ways. Flooding exposes skin to contaminated water, promoting infections. Heat waves increase sweating and heat-related skin conditions. Droughts and water scarcity compromise hygiene and promote skin infections.

For Bangladesh specifically, climate change poses significant threats to skin health. Bangladesh is particularly vulnerable to climate change impacts due to its low elevation, high population density, and dependence on monsoon rainfall. Sea level rise threatens coastal populations. More intense monsoons and cyclones increase flooding frequency.

Skin diseases associated with flooding in Bangladesh include tinea pedis, wound infections, folliculitis, and contact dermatitis from contaminated floodwater containing agricultural chemicals and sewage.

Ultraviolet radiation, another climate-related factor, is expected to increase in some regions as the ozone layer is affected by climate change. Increased UV exposure raises risks of sunburn and skin cancer, particularly for depigmented skin (as in vitiligo) which lacks melanin protection.

Addressing the skin health impacts of climate change requires both mitigation (reducing greenhouse gas emissions) and adaptation strategies (improved healthcare preparedness, community resilience).
""",

    # ── DGHS — ADDITIONAL ────────────────────────────────────────────────────
    "dghs_skin_monsoon_01.txt": """SOURCE: DGHS
TOPIC: Monsoon Season Skin Diseases in Bangladesh
---
The monsoon season (June to September) in Bangladesh creates unique challenges for skin disease management. Flooding, high humidity, and heavy rainfall promote conditions favorable for infectious skin diseases and worsen existing skin conditions.

Tinea pedis (athlete's foot) is particularly common during and after monsoon flooding. Walking through floodwater — which is often contaminated with soil, agricultural chemicals, and sewage — damages skin and introduces fungal and bacterial pathogens. People in rural areas who walk barefoot through flooded fields are at very high risk.

Scabies transmission accelerates during monsoon season when overcrowding in raised structures during flooding brings large numbers of people into close contact. Temporary shelters and cyclone centers often facilitate rapid scabies transmission.

Wound infections are a major concern during flooding. Minor cuts and abrasions become contaminated with floodwater bacteria including gram-negative organisms. Necrotizing fasciitis from wound contamination with floodwater has been reported.

Folliculitis — infection of hair follicles — is common during monsoon season due to occlusion of follicles by sweat, mud, and clothing. The back, buttocks, and thighs are commonly affected.

Prickly heat (miliaria) affects many people during the hot, humid pre-monsoon and monsoon periods. Blocked sweat glands cause small, itchy papules and blisters. Keeping skin cool and dry is the primary management strategy.

DGHS guidance for monsoon skin disease prevention includes: wearing rubber footwear when walking through floodwater, drying skin thoroughly after water exposure, washing with clean water and soap after flood exposure, treating any wounds promptly, and seeking care for any spreading skin infection.
""",
    "dghs_skin_children_bd_01.txt": """SOURCE: DGHS
TOPIC: Common Skin Diseases in Bangladeshi Children
---
Children in Bangladesh bear a disproportionate burden of skin disease. A combination of biological vulnerability, environmental factors, and limited healthcare access drives high rates of infectious and inflammatory skin conditions in the pediatric population.

Scabies is among the most prevalent skin conditions in Bangladeshi children, particularly those in rural areas, slums, and boarding educational institutions (madrasas). Studies report prevalence rates of fifteen to fifty percent in high-risk settings. School-age children are most commonly affected.

Tinea capitis (scalp ringworm) is a significant concern in school-age children. Sharing combs, hair accessories, and hats facilitates spread. Without treatment, tinea capitis can cause permanent alopecia. Outbreaks in schools are common.

Impetigo — a superficial bacterial skin infection caused by Staphylococcus aureus and Streptococcus pyogenes — is extremely common in young children in Bangladesh. The hot, humid climate, insect bites, minor skin injuries, and existing skin conditions like scabies and eczema create entry points for infection.

Molluscum contagiosum — a viral skin infection — is common in school-age children and spreads in swimming pools and through direct contact. In children with atopic dermatitis, it can spread widely across eczematous skin.

Miliaria (prickly heat) affects many infants and young children in Bangladesh's hot climate. Blocked sweat glands cause itchy, red papules. Keeping the infant cool and wearing loose, light clothing prevents and treats miliaria.

DGHS school health programs include routine skin inspection for common conditions and referral protocols for tinea capitis, scabies, and impetigo. Training school health teachers to recognize common skin conditions enables earlier identification and treatment.
""",
    "dghs_telemedicine_skin_01.txt": """SOURCE: DGHS
TOPIC: Telemedicine and Digital Health for Skin Disease in Bangladesh
---
Bangladesh has made significant strides in integrating telemedicine into its healthcare system, particularly to address the shortage of specialist physicians in rural areas. Dermatology is a specialty particularly well-suited to telemedicine because diagnosis often relies on visual assessment of skin lesions.

The Government of Bangladesh launched Shastho Batayon — a national telemedicine service — providing remote physician consultations via telephone and video. Dermatological consultations have been a component of this service. During the COVID-19 pandemic, telemedicine usage expanded substantially.

Mobile health (mHealth) applications for skin disease management are emerging in Bangladesh. Applications that allow community health workers to photograph skin lesions and transmit images to dermatologists for remote assessment are being piloted. This approach can dramatically improve access to dermatological expertise in rural areas.

Artificial intelligence-assisted skin disease diagnosis represents a promising frontier for Bangladesh's healthcare challenges. AI tools trained on local clinical data — such as those developed using Bangladeshi clinical datasets from medical college hospitals in Faridpur and Rangpur — have the potential to provide decision support at the primary care level.

AI-powered screening and triage tools, accessible via smartphone or tablet, could extend the reach of dermatological expertise to community clinics, upazila health complexes, and even community-level health workers. Such tools should be designed to support — not replace — clinical judgment, guiding patients to the appropriate level of care.

DGHS digital health strategy includes integration of AI-assisted diagnostic tools into the health system, subject to appropriate validation, regulatory review, and ongoing monitoring of performance and safety. Ensuring equitable access to digital health tools for rural and underserved populations is a priority.
""",
    "dghs_skin_prevention_01.txt": """SOURCE: DGHS
TOPIC: Skin Disease Prevention — National Public Health Approach Bangladesh
---
Preventing common skin diseases requires a multi-level approach addressing individual behaviors, household practices, community factors, and health system capacity. The Directorate General of Health Services Bangladesh integrates skin disease prevention into national public health programs.

At the individual and household level, DGHS promotes awareness of skin disease transmission, symptoms, and prevention through the national health education system. Key messages include the importance of daily bathing, not sharing personal items, wearing footwear, recognizing common skin disease signs, and seeking early treatment rather than self-medicating with inappropriate products.

School health programs address the high burden of skin disease in children. Health education sessions in schools cover hygiene, recognition of common conditions, and when to seek care. School health inspections by health assistants identify affected children for referral and treatment.

Community-level prevention addresses environmental factors that promote skin disease. Safe water and sanitation programs reduce the burden of infectious skin conditions. Improved housing quality reduces overcrowding that facilitates scabies transmission. Agricultural extension programs promote safe handling of pesticides and protective equipment to reduce occupational contact dermatitis.

Health system capacity building includes training of healthcare workers at all levels in recognition and management of common skin diseases, ensuring consistent availability of essential dermatological medicines in the public health system, and developing clear referral protocols.

National disease surveillance programs monitor trends in skin disease burden. Surveillance data guide public health planning and resource allocation.

Integration of skin disease management with existing vertical programs — maternal and child health, nutrition, school health, and NTD control — maximizes efficiency and coverage.
""",
    "dghs_skin_elderly_bd_01.txt": """SOURCE: DGHS
TOPIC: Skin Diseases in Elderly Bangladeshis
---
Elderly people in Bangladesh face distinct skin disease challenges related to physiological changes in aging skin, comorbid conditions, and the particular social context of elderly care in Bangladesh.

Aging skin undergoes significant changes that increase susceptibility to skin disease. Sebum production decreases, leading to drier skin that is more susceptible to irritation and infection. The skin barrier becomes less efficient. Immune responses are less robust, making infections more severe and harder to clear.

Scabies in elderly Bangladeshis often presents atypically. Classic burrows may be absent. The rash may be non-specific and widespread. Nursing home residents and those in institutional care are particularly vulnerable.

Venous stasis dermatitis — inflammation of the lower leg skin related to poor venous return — is common in elderly patients. It presents as brownish, scaly skin on the lower legs, sometimes with weeping and ulceration. Management requires compression bandaging, emollients, and treatment of secondary infection.

Lichen simplex chronicus — thickened skin from chronic scratching — is common in older adults with chronic itch due to dry skin or other conditions.

Bullous pemphigoid — an autoimmune blistering condition — predominantly affects elderly individuals. It presents with large, tense blisters on the skin. It requires prompt diagnosis and specialist management with immunosuppressive therapy.

Skin cancer, particularly squamous cell carcinoma, is a concern in elderly Bangladeshis with history of sun exposure. While skin cancer is less common in darker-skinned populations, it is not negligible and tends to present at more advanced stages.

Elderly patients in Bangladesh may face barriers to skin care access including mobility limitations, transportation difficulties, and financial constraints. Mobile health camps and telemedicine services are particularly valuable for this population.
""",
    "dghs_dghs_education_01.txt": """SOURCE: DGHS
TOPIC: DGHS Skin Disease Awareness Programs
---
The Directorate General of Health Services Bangladesh conducts and supports various public awareness programs targeting common skin diseases. These programs aim to reduce stigma, improve early recognition, and promote appropriate health-seeking behavior.

National health campaigns addressing skin diseases are conducted through television, radio, print media, and social media platforms. Key messages target common misconceptions — particularly the belief that vitiligo is contagious or related to leprosy, that scabies is caused by poor character rather than a mite, and that ringworm is caused by worms.

Mobile health outreach teams conduct skin disease camps in rural and peri-urban areas, providing free consultation, diagnosis, and treatment. These camps are particularly targeted at communities with limited healthcare access and high prevalence of skin diseases.

DGHS supports dermatology residency training at medical college hospitals throughout Bangladesh to increase the number of trained dermatologists. The Bangladesh College of Physicians and Surgeons (BCPS) oversees post-graduate dermatology training.

Integration of dermatology content into the training curriculum of medical officers, community health workers, and nurses at all levels of the health system improves primary-level skin disease management.

Community engagement through local government institutions (union parishads), mosques, and women's groups is used to disseminate skin health messages in rural communities. Respected community figures — religious leaders, teachers, local government officials — are engaged as health messengers.

Youth engagement programs include skin disease awareness in secondary school curricula and activities by student health clubs. Educating children and adolescents creates long-term health awareness that persists into adulthood.

DGHS collaborates with international partners including WHO, UNICEF, and international NGOs to conduct skin disease surveys, training programs, and public health campaigns.
""",
    # ── WHO — ADDITIONAL 2 ───────────────────────────────────────────────────
    "who_contact_dermatitis_01.txt": """SOURCE: WHO
TOPIC: WHO Perspective — Occupational Skin Diseases
---
Occupational skin diseases represent a significant proportion of all occupational diseases worldwide. The World Health Organization recognizes occupational contact dermatitis as an important preventable cause of morbidity and lost productivity. Contact dermatitis accounts for approximately ninety percent of all occupational skin diseases.

WHO estimates that occupational skin diseases affect millions of workers globally each year. High-risk sectors include healthcare, construction, food processing, agriculture, hairdressing, and metal working. In Bangladesh, the ready-made garment (RMG) sector — employing over four million workers, predominantly women — and the agricultural sector present the greatest occupational skin disease burden.

The economic impact of occupational skin diseases is substantial. Workers may require time off, change jobs, or permanently leave affected industries. Productivity losses, medical costs, and workers' compensation claims represent measurable economic burdens.

Prevention of occupational contact dermatitis follows the hierarchy of controls. Elimination or substitution of hazardous substances is the most effective approach. Engineering controls — ventilation, automated handling of chemical — reduce exposure. Administrative controls — job rotation, reducing wet work duration — can lower risk. Personal protective equipment, including appropriate gloves and barrier creams, provides the final layer of protection.

WHO recommends integrating occupational skin disease surveillance into national occupational health programs. Reporting and recording of occupational skin diseases enables identification of high-risk workplaces and industries and targets preventive interventions.

For Bangladesh, strengthening occupational health services in the garment and agricultural sectors, and training occupational health officers in skin disease prevention and management, are WHO-endorsed priorities.
""",
    "who_general_skin_01.txt": """SOURCE: WHO
TOPIC: WHO Integrated Approach to Skin Health in Primary Care
---
Skin diseases are among the most common reasons for primary healthcare consultations worldwide, yet they receive disproportionately little attention in health system planning. The World Health Organization advocates for a comprehensive, integrated approach to skin health within primary care.

Integrating skin disease management into primary care reduces unnecessary specialist referrals, improves timely access to treatment, and reduces costs for patients and health systems. The majority of common skin diseases — including tinea, scabies, contact dermatitis, seborrheic dermatitis, and mild atopic dermatitis — can be effectively managed at the primary care level by trained generalists.

WHO recommendations for integrating skin health into primary care include: incorporating basic dermatology into undergraduate and postgraduate medical and nursing curricula; providing continuing education for primary care providers on recognition and management of common skin diseases; developing and disseminating clinical practice guidelines adapted to local disease burden and available resources; ensuring essential dermatological medicines are available in primary care facilities; and establishing clear referral pathways for cases requiring specialist care.

Task-sharing between physicians, nurses, and community health workers can extend dermatological service delivery at lower cost. Community health workers trained to recognize and manage common skin diseases (scabies, tinea, impetigo) and to refer complex cases can significantly expand access in resource-limited settings.

Digital health tools, including teledermatology and AI-assisted diagnosis, offer additional opportunities to extend dermatological expertise to primary care. WHO supports appropriate validation and implementation of such tools to improve skin disease management in underserved settings.
""",
    "who_seborrheic_01.txt": """SOURCE: WHO
TOPIC: Seborrheic Dermatitis — Global and Regional Perspectives
---
Seborrheic dermatitis is a chronic relapsing inflammatory skin condition that affects populations worldwide, with no significant geographic predilection. Its global prevalence is estimated at one to three percent in immunocompetent adults, with significantly higher rates in specific populations.

Immunocompromised individuals bear a disproportionate burden. In people with HIV infection, seborrheic dermatitis affects thirty to eighty percent, compared to one to three percent in the general population. Its severity correlates with degree of immunosuppression. In many settings, severe seborrheic dermatitis may be a marker for undiagnosed HIV infection.

In South and Southeast Asia, including Bangladesh, the warm and humid climate promotes Malassezia yeast proliferation and may increase seborrheic dermatitis prevalence and severity, though systematic epidemiological data from these regions are limited.

Cultural hair care practices prevalent in South Asia — including frequent application of hair oils (coconut, mustard, sesame) — may worsen seborrheic dermatitis by providing lipid substrates for Malassezia growth. Educating patients about this relationship is important in cultural contexts where oil application is a deeply embedded practice.

WHO essential medicines for seborrheic dermatitis — including ketoconazole shampoo and hydrocortisone cream — are widely available. Access barriers relate more to cost and healthcare access than availability.

Integration of seborrheic dermatitis management into HIV care programs is an important strategy for improving quality of life in people living with HIV. Dermatological care should be part of comprehensive HIV management.
""",
    "who_vitiligo_02.txt": """SOURCE: WHO
TOPIC: WHO Mental Health and Chronic Skin Conditions
---
The World Health Organization recognizes a strong bidirectional relationship between mental health and chronic skin conditions. Conditions like vitiligo, atopic dermatitis, and psoriasis carry significant psychological burden, while mental health conditions can worsen skin disease through multiple mechanisms.

The psychological impact of visible skin conditions is particularly profound in social contexts where skin appearance carries significant cultural meaning, as in many South Asian societies including Bangladesh. Social exclusion, employment discrimination, and marriage difficulties associated with visible skin conditions contribute to depression, anxiety, and reduced quality of life.

WHO's integrated care approach advocates for routine psychological screening in dermatological settings. Simple validated tools such as the Dermatology Life Quality Index (DLQI) can efficiently assess the impact of skin conditions on patients' daily lives and prompt referral for psychological support when needed.

Psychological interventions that benefit patients with chronic skin conditions include cognitive-behavioral therapy (addressing maladaptive thoughts about appearance), mindfulness-based approaches (reducing stress reactivity), group therapy and peer support groups, and integrated acceptance and commitment therapy.

Community-level interventions to reduce stigma around skin conditions are also important. Public health campaigns that accurately portray vitiligo, eczema, and other skin conditions can reduce discrimination and create more inclusive social environments.

Healthcare provider training in recognizing and addressing the psychosocial dimensions of skin disease is essential. Dermatologists, general practitioners, and community health workers should be equipped to identify psychological distress and facilitate access to support.

In Bangladesh, expanding access to mental health services generally — and specifically integrating psychological support into dermatological care at district hospital and medical college levels — is a priority.
""",

    # ── NIH — ADDITIONAL ─────────────────────────────────────────────────────
    "nih_general_skincare_01.txt": """SOURCE: NIH
TOPIC: Basic Skin Care and Skin Health
---
The skin is the body's largest organ and serves as the primary barrier against the external environment. Maintaining healthy skin requires consistent daily care practices that preserve the skin barrier, prevent infection, and address environmental challenges.

Cleansing is fundamental to skin health. Daily bathing removes sweat, sebum, bacteria, and environmental pollutants from the skin surface. Use lukewarm water — hot water strips natural skin oils and worsens dryness. Use a mild, pH-balanced cleanser. Avoid harsh scrubbing that damages the skin barrier.

Moisturization maintains skin barrier function and prevents dryness. Apply moisturizer to slightly damp skin after bathing to lock in moisture. Thick creams and ointments are more effective than thin lotions for dry skin conditions. Look for ingredients like ceramides, glycerin, urea, or petroleum jelly.

Sun protection is essential for all skin types. Ultraviolet radiation causes premature aging, hyperpigmentation, and skin cancer. Apply broad-spectrum sunscreen (SPF 30 or higher) to sun-exposed areas when outdoors. Protective clothing, hats, and shade provide additional protection.

Diet and hydration influence skin health. Adequate water intake supports skin hydration. A balanced diet rich in antioxidants (fruits, vegetables) provides nutrients important for skin cell function and repair. Omega-3 fatty acids found in fish and flaxseed support skin barrier integrity.

Avoiding smoking and limiting alcohol intake benefit skin health. Smoking impairs blood flow to skin, promotes wrinkles, and increases infection risk. Alcohol dehydrates skin and can trigger rosacea and psoriasis flares.

Adequate sleep allows skin to repair and regenerate. Growth hormone released during deep sleep stimulates skin cell turnover and collagen production.

In Bangladesh's climate, adapting skincare to seasonal changes — heavier moisturizers in the dry winter, lighter products in the humid summer — is important for maintaining skin health throughout the year.
""",
    "nih_when_to_see_doctor_01.txt": """SOURCE: NIH
TOPIC: When to See a Doctor for Skin Problems
---
Most minor skin conditions can be managed at home with over-the-counter products. However, certain signs and symptoms indicate the need for professional medical evaluation. Knowing when to seek care can prevent complications and ensure appropriate treatment.

Seek medical evaluation promptly when: a rash spreads rapidly or covers a large area of the body; the skin condition is accompanied by fever, chills, or feels very unwell; the rash does not improve after two weeks of appropriate over-the-counter treatment; blisters develop that are not explained by a known cause; signs of bacterial infection appear (increasing redness, warmth, swelling, pus, streaks radiating from the area, or fever); the rash affects sensitive areas including the face, eyes, genitals, or mouth; the skin condition significantly affects sleep, daily activities, or emotional wellbeing.

Seek urgent or emergency care when: a rash develops with difficulty breathing, throat swelling, or dizziness, which may indicate anaphylaxis; the rash spreads extremely rapidly over hours with severe pain and the skin blisters or becomes necrotic; high fever accompanies the skin condition; widespread blistering or skin loss occurs (may indicate Stevens-Johnson syndrome or toxic epidermal necrolysis).

For specific conditions: scalp ringworm in children always requires medical evaluation because it needs oral antifungal treatment and can cause permanent hair loss. Any spreading or treatment-resistant skin condition, suspected scabies in a child, and any skin condition in a person with HIV or diabetes warrants early medical attention.

In Bangladesh, the nearest community clinic or upazila health complex is the appropriate first point of contact for skin conditions requiring professional evaluation. Healthcare workers at these facilities are equipped to manage most common skin conditions and can refer complex cases appropriately.
""",
    "nih_skin_microbiome_01.txt": """SOURCE: NIH
TOPIC: Skin Microbiome and Skin Disease
---
The skin hosts a diverse community of microorganisms — bacteria, fungi, viruses, and mites — collectively known as the skin microbiome. This microbial community plays an important role in skin health, immune development, and protection against pathogens.

The composition of the skin microbiome varies by body site. Sebaceous (oil-rich) areas like the face and chest are dominated by Cutibacterium (formerly Propionibacterium) species. Moist areas like armpits and toe webs harbor Staphylococcus and Corynebacterium species. Malassezia fungi dominate sebum-rich areas.

In healthy skin, the microbiome forms a protective ecological community that excludes pathogenic organisms through competition for nutrients, production of antimicrobial substances, and stimulation of the host immune system. Disruption of this community can predispose to skin disease.

In atopic dermatitis, the skin microbiome is significantly altered. Staphylococcus aureus — an uncommon colonizer of healthy skin — predominates in affected skin. Staphylococcal toxins trigger immune activation and worsening inflammation. Rebalancing the skin microbiome through treatment of atopic dermatitis shifts the community back toward Staphylococcus epidermidis and other commensal species.

In seborrheic dermatitis, overgrowth of Malassezia yeast — which is part of the normal skin flora — in the context of excess sebum and impaired host response drives inflammation.

In tinea infections, dermatophytes displace the normal skin flora through keratin degradation and immunomodulation.

Understanding the skin microbiome opens new approaches to treating skin disease through microbiome restoration — the use of probiotic bacteria applied to skin to restore healthy microbial ecology.
""",
    "nih_eczema_adult_01.txt": """SOURCE: NIH
TOPIC: Atopic Dermatitis in Adults
---
While atopic dermatitis is most commonly recognized as a childhood condition, it persists into adulthood in a significant proportion of cases and can first present in adults. Adult atopic dermatitis presents distinct clinical features and management challenges compared to childhood disease.

Adults with persistent atopic dermatitis often have different distribution patterns than children. Hand and neck involvement is particularly common. Prurigo nodularis — intensely itchy, thickened nodules from chronic scratching — is a prominent feature in some adults with long-standing disease.

Adult-onset atopic dermatitis — presenting for the first time in adults with no childhood history — is recognized with increasing frequency. It may be triggered by occupational exposures, environmental changes, or hormonal factors. Adult-onset disease tends to be more severe and less responsive to standard treatments than childhood-onset disease.

The psychological burden of atopic dermatitis in adults is substantial. Adults must manage the condition while maintaining professional and social functioning. Visible skin changes, chronic itch, and sleep disruption affect work performance, relationships, and quality of life. Depression and anxiety are significantly more common in adults with atopic dermatitis than in the general population.

In Bangladesh, adults with atopic dermatitis face additional challenges from the tropical climate. Hot, humid conditions promote sweating that irritates affected skin. Occupational exposures — agricultural chemicals, industrial solvents, construction materials — often worsen the condition.

Systemic treatment options for moderate to severe adult atopic dermatitis include traditional immunosuppressants (cyclosporine, methotrexate, mycophenolate mofetil) and newer biologics (dupilumab, tralokinumab). Access to biologics is extremely limited in Bangladesh due to cost.
""",
    "nih_skin_nutrition_01.txt": """SOURCE: NIH
TOPIC: Nutrition and Skin Health
---
Adequate nutrition is fundamental to healthy skin function and recovery from skin disease. Nutritional deficiencies can both cause and worsen a variety of skin conditions.

Protein deficiency impairs wound healing and skin barrier integrity. Adequate protein intake is essential for skin cell repair and regeneration. Malnutrition — common in rural Bangladesh — compromises skin health and increases susceptibility to infection.

Iron deficiency anemia is associated with pale skin, hair thinning, and brittle nails. Angular cheilitis (cracking at the corners of the mouth) is a classic sign of iron deficiency.

Zinc deficiency causes acrodermatitis enteropathica, characterized by skin lesions around body orifices and extremities, hair loss, and diarrhea. Zinc is important for skin repair, immune function, and anti-inflammatory activity. Zinc supplementation can improve chronic skin ulcers.

Vitamin C (ascorbic acid) is essential for collagen synthesis. Deficiency (scurvy) causes perifollicular hemorrhages, corkscrew hairs, and impaired wound healing.

Vitamin D plays important roles in skin immune function and barrier integrity. Vitamin D deficiency has been associated with increased susceptibility to skin infections and worsening of atopic dermatitis.

Omega-3 fatty acids from fish oil have anti-inflammatory properties and may help reduce atopic dermatitis severity. Populations with high fish consumption show lower rates of atopic conditions.

In Bangladesh, nutritional deficiencies — particularly iron, zinc, and vitamin D — remain prevalent in rural populations and contribute to skin disease burden. Addressing nutritional deficiencies as part of comprehensive skin disease management is important.

Probiotic supplementation, particularly Lactobacillus species, shows promise in reducing atopic dermatitis severity in infants and children by modulating the immune response.
""",
    "nih_itch_management_01.txt": """SOURCE: NIH
TOPIC: Understanding and Managing Chronic Itch (Pruritus)
---
Chronic itch (pruritus) lasting more than six weeks is one of the most debilitating symptoms in dermatology. It is a cardinal feature of atopic dermatitis, scabies, contact dermatitis, and many other skin conditions. Untreated chronic itch severely impacts quality of life, causes sleep disruption, and drives the scratch-skin damage cycle that worsens many skin conditions.

Itch is mediated by specialized C-nerve fibers in the skin that transmit itch signals to the spinal cord and brain. The sensation shares neural pathways with pain but is a distinct sensation. Histamine is one mediator of itch, but many other molecules are involved — including IL-31, substance P, and proteases — explaining why antihistamines do not fully control itch in conditions like atopic dermatitis.

The itch-scratch cycle is central to skin disease progression. Scratching provides temporary relief but damages the skin barrier, worsens inflammation, and releases more itch mediators. Breaking this cycle is a key therapeutic goal.

Non-pharmacological approaches to itch include keeping skin cool (heat worsens itch), applying cold compresses, keeping fingernails short and smooth, wearing cool, loose-fitting clothing, and distraction techniques. Cognitive-behavioral therapy can help patients modify scratching behavior.

Topical treatments for itch include menthol creams (cooling sensation), capsaicin cream (desensitizes itch nerve fibers), topical calcineurin inhibitors, and topical corticosteroids. Topical anesthetics provide temporary relief.

Systemic antihistamines (cetirizine, fexofenadine, chlorpheniramine) help control histamine-mediated itch. Sedating antihistamines (hydroxyzine, chlorpheniramine) improve nighttime itching and sleep.

In severe chronic itch, dupilumab and other newer targeted therapies provide significant itch reduction by targeting inflammatory pathways.
""",
    "nih_phototherapy_01.txt": """SOURCE: NIH
TOPIC: Phototherapy for Skin Diseases
---
Phototherapy — the therapeutic use of ultraviolet light — is an effective treatment for several chronic skin diseases including vitiligo, atopic dermatitis, psoriasis, and mycosis fungoides. It is delivered in controlled clinical settings using specialized light-emitting equipment.

Narrowband ultraviolet B (NB-UVB) phototherapy, which emits UV light at 311-313 nanometers, is the most widely used form of phototherapy. It is effective for vitiligo (inducing repigmentation through melanocyte stimulation), atopic dermatitis (reducing inflammation), and psoriasis (normalizing skin cell turnover).

NB-UVB phototherapy requires multiple sessions per week — typically two to three — over months. Initial sessions use very low UV doses that are gradually increased based on individual skin response. The main side effects are temporary redness, itching, and potential long-term increase in skin cancer risk with very prolonged cumulative exposure.

Psoralen plus UVA (PUVA) therapy combines a photosensitizing medication (psoralen) with UVA exposure. It is effective for severe psoriasis and has been used for vitiligo, but its use has declined due to increased cancer risk with long-term use compared to NB-UVB.

Targeted phototherapy using the excimer laser (308 nm) delivers UVB to specific skin areas. It is effective for localized vitiligo and psoriasis, requiring fewer sessions than whole-body phototherapy.

In Bangladesh, phototherapy equipment is available at medical college hospitals in major cities (Dhaka, Chittagong, Rajshahi, etc.). Rural patients requiring phototherapy must travel to access it — a major access barrier for conditions like vitiligo and severe atopic dermatitis requiring prolonged treatment courses.

Expanding phototherapy access through district hospitals and telemedicine-guided protocols is a priority in Bangladesh's dermatology service development.
""",

    "cdc_seborrheic_dermatitis_03.txt": """SOURCE: CDC
TOPIC: Seborrheic Dermatitis — Neurological Associations and Special Populations
---
Seborrheic dermatitis has significant associations with several neurological and systemic conditions. Understanding these associations guides appropriate evaluation and management.

Parkinson's disease is the most established neurological association with seborrheic dermatitis. People with Parkinson's disease have a markedly higher prevalence and more severe seborrheic dermatitis. Autonomic dysfunction in Parkinson's disease leads to increased sebum production. Reduced facial expression may result in sebum accumulation in facial skin folds. Certain Parkinson's medications may also contribute.

People with HIV infection have dramatically increased prevalence and severity of seborrheic dermatitis. In some HIV-positive individuals, severe seborrheic dermatitis is the presenting sign of underlying immunosuppression. The severity of seborrheic dermatitis correlates with CD4 count — worsening as immunity declines. With effective antiretroviral therapy, seborrheic dermatitis often improves.

Facial nerve palsy — weakness of facial muscles causing asymmetric expression — can result in sebum accumulation on the paretic side, predisposing to seborrheic dermatitis on that side.

Spinal cord injuries affecting autonomic function can alter sebum production and contribute to seborrheic dermatitis.

Some medications trigger seborrheic dermatitis as a side effect. Lithium carbonate (used for bipolar disorder), psoralen, some interferon preparations, and certain antipsychotic medications have been associated with onset or worsening of seborrheic dermatitis.

Nutritional deficiencies, including zinc and B vitamin deficiencies, can cause skin changes resembling seborrheic dermatitis. Nutritional assessment is warranted when seborrheic dermatitis presents with atypical features or is refractory to standard treatment.
""",
    "dghs_garment_skin_01.txt": """SOURCE: DGHS
TOPIC: Skin Diseases in Bangladesh's Garment Sector Workers
---
Bangladesh's ready-made garment (RMG) sector is one of the world's largest, employing over four million workers — predominantly women — and accounting for over eighty percent of the country's export earnings. Skin diseases represent a significant occupational health challenge in this sector.

Garment workers are exposed to a variety of potential skin irritants and sensitizers. Fabric dyes — particularly reactive dyes and disperse dyes — can cause both irritant and allergic contact dermatitis. Azo dyes are the most widely used in Bangladesh's textile industry and are potential sensitizers. Formaldehyde-based finishing agents used to make fabrics wrinkle-resistant are skin irritants and potential allergens.

Rubber chemicals in elastic waistbands, gloves, and machinery components are common occupational allergens. Latex sensitivity, while less common than in healthcare workers, is encountered in garment workers using latex gloves.

Physical factors in garment factories contribute to skin disease. Prolonged sitting in hot factory conditions causes sweating and friction dermatitis on the thighs and buttocks. Repetitive hand movements cause calluses, friction blisters, and hand dermatitis. Air conditioning systems, where present, can cause excessive skin dryness.

Many garment factories in Bangladesh lack adequate occupational health services. Workers with skin conditions may continue working due to economic necessity, worsening their condition and spreading infectious skin diseases to co-workers.

DGHS recommends that garment sector employers implement occupational health programs including skin disease screening, provision of appropriate personal protective equipment, substitution of known sensitizers where possible, and access to occupational health professionals.

Worker education about skin disease recognition and prevention is an important component of garment sector occupational health programs.
""",
    "dghs_rahim_narrative_01.txt": """SOURCE: DGHS
TOPIC: Patient Navigation in Bangladesh's Health System — A Practical Guide
---
Understanding how to navigate Bangladesh's health system is essential for patients with skin diseases to access appropriate care efficiently without unnecessary delay or expense.

For most skin conditions of mild to moderate severity, the first point of contact should be the community clinic (kaminuniti klinik) at the union level or, in urban areas, a government dispensary. Community clinics are staffed by community health care providers who can manage common conditions including scabies, tinea, and impetigo, and can dispense essential medicines. These services are free for registered community members.

For conditions that require physician evaluation — widespread or treatment-resistant conditions, suspected tinea capitis, atopic dermatitis requiring prescription treatment — the upazila health complex (UHC) provides free or highly subsidized outpatient consultation and medicines. Every upazila has a health complex accessible within the administrative area.

District hospitals, located in the administrative district headquarters, provide a higher level of care with specialist physicians. Patients referred from UHC level with complex or refractory skin disease are seen here. Referral letters from the UHC facilitate efficient evaluation.

For specialist dermatology, patients are referred to medical college hospitals in divisional cities. These hospitals have dermatology departments with consultant dermatologists, phototherapy equipment, and facilities for patch testing and advanced investigations.

Private dermatology practice is available in cities and larger towns. Quality varies. Private consultation involves out-of-pocket costs that can be prohibitive for low-income patients.

When in doubt about where to go, the nearest government health facility is the appropriate starting point. Bringing any previous prescriptions, test results, and a brief written description of the problem — or using a digital health tool like SkinAI Bangladesh for initial triage — helps ensure efficient evaluation at each level of the health system.
""",

    "cdc_scabies_07.txt": """SOURCE: CDC
TOPIC: Scabies — Global Distribution and Epidemiology
---
Scabies is a global public health problem affecting more than two hundred million people at any given time. It is endemic in many tropical and subtropical regions and can reach epidemic proportions in overcrowded settings.

Scabies occurs across all socioeconomic levels and climates, but its burden is greatest in resource-limited settings in sub-Saharan Africa, South and Southeast Asia (including Bangladesh), the Pacific Islands, and Latin America. In endemic communities, the prevalence among children can exceed fifty percent.

The global burden of scabies extends beyond the immediate discomfort of infestation. Secondary bacterial infections — the most significant complication — contribute substantially to the burden of bacterial skin disease, septicemia, and post-streptococcal glomerulonephritis in endemic regions.

Scabies epidemiology shows cyclical patterns, with outbreaks occurring every ten to fifteen years in some populations. The reasons for these cycles are not fully understood but may relate to herd immunity and population density dynamics.

Institutional outbreaks are a distinct epidemiological pattern. Nursing homes, hospitals, prisons, refugee camps, and boarding schools facilitate rapid scabies transmission due to close contact and delayed recognition.

In conflict-affected areas and refugee camps, scabies rates can be extremely high — sometimes exceeding seventy percent — due to overcrowding, limited access to water and sanitation, and disrupted healthcare.

Climate may influence scabies distribution. Warmer temperatures increase mite survival on surfaces and potentially expand the zone of endemicity. Climate change could worsen the global scabies burden.

The COVID-19 pandemic disrupted scabies control programs globally, and subsequent increases in scabies cases were reported in many countries, including in Europe and Asia.
""",

    "nih_skin_color_01.txt": """SOURCE: NIH
TOPIC: Skin Disease Recognition in Darker Skin Tones
---
Many dermatological texts and resources describe skin disease appearances primarily in fair-skinned populations, yet the majority of the world's population — including in Bangladesh — has darker skin tones. Skin disease presentation can differ significantly in darker skin, and recognizing these differences is essential for accurate diagnosis.

In darker skin (Fitzpatrick types IV-VI, common in Bangladesh), erythema (redness) may not appear red but rather as a darker hue, purplish or brownish discoloration. Inflammation is harder to detect visually, potentially delaying diagnosis. Tinea infections may appear brown rather than the classic pink-red ring.

Post-inflammatory hyperpigmentation (PIH) — darkening of skin following inflammation or injury — is much more common and more pronounced in darker skin tones. It can persist for months to years after the original skin condition has resolved. PIH from acne, eczema, and other skin conditions causes significant distress in darker-skinned patients.

Post-inflammatory hypopigmentation — lightening following skin inflammation — also occurs more frequently in darker skin. It can be confused with vitiligo or other depigmenting conditions.

Vitiligo is particularly visible in darker-skinned individuals, as the contrast between depigmented patches and surrounding skin is striking. This contributes to the significant social impact of vitiligo in Bangladesh and other South Asian countries.

Healthcare providers serving primarily darker-skinned patients — as in Bangladesh — require specific training in recognizing skin disease presentations appropriate to their patient population. AI diagnostic tools developed for dermatology should be trained on diverse skin tone datasets to avoid diagnostic bias.

The BD-SkinNet model, trained on clinical data from Bangladeshi medical college hospitals (Faridpur and Rangpur), is specifically designed to recognize skin disease presentations in Bangladeshi skin tones.
""",

    "dghs_skin_emergency_bd_01.txt": """SOURCE: DGHS
TOPIC: Skin Disease Emergencies — When to Seek Urgent Care in Bangladesh
---
TOPIC: Bacterial Skin Infections — Impetigo, Cellulitis, Folliculitis
---
Bacterial skin infections are among the most common infectious diseases worldwide. Staphylococcus aureus and Streptococcus pyogenes (Group A Streptococcus) are the most frequent causative organisms.

Impetigo is a superficial bacterial skin infection most common in children. It presents as honey-colored, crusting lesions, typically on the face around the nose and mouth. It spreads easily through direct contact and is highly contagious in school settings. Bullous impetigo, caused by toxin-producing Staphyloccus aureus, produces fragile blisters that rupture and leave raw areas. Treatment with topical mupirocin or systemic antibiotics clears most cases rapidly.

Cellulitis is a bacterial infection of the deeper layers of the skin (dermis and subcutaneous tissue). It presents as a rapidly spreading area of redness, warmth, swelling, and tenderness, usually on a limb. Fever may be present. It requires systemic antibiotic treatment.

Folliculitis is infection of hair follicles, presenting as red, tender papules or pustules at the base of hairs. It commonly affects the back, thighs, and buttocks. Mild cases resolve with improved hygiene; extensive cases require topical or oral antibiotics.

Furuncles (boils) are deeper infections of individual hair follicles. They present as painful, pus-filled nodules. Treatment with warm compresses, incision and drainage, and sometimes antibiotics resolves most cases.

In Bangladesh, humid climate and skin trauma from insect bites, scabies scratching, and cuts create frequent entry points for bacteria. Secondary bacterial infection complicating scabies and eczema is particularly common. Any worsening, spreading skin infection with systemic signs should be referred promptly.
""",

    "dghs_skin_emergency_bd_01.txt": """SOURCE: DGHS
TOPIC: Skin Disease Emergencies — When to Seek Urgent Care in Bangladesh
---
While most skin diseases in Bangladesh are managed in outpatient settings, certain skin conditions represent medical emergencies requiring urgent hospital care. Healthcare workers and community members should be able to recognize emergency warning signs.

Anaphylaxis — a severe allergic reaction affecting the whole body — can follow insect stings, medications, or food exposure. Signs include rapid-onset hives, swelling of the face and throat, breathing difficulty, and collapse. Anaphylaxis is a life-threatening emergency requiring immediate treatment with epinephrine (adrenaline) and urgent transfer to hospital.

Necrotizing fasciitis is a rapidly spreading, life-threatening bacterial infection of the deep skin and soft tissues. It presents as rapidly spreading redness, severe pain disproportionate to visible findings, fever, and rapidly worsening condition. Early surgical debridement and systemic antibiotics are required. Any patient with rapidly spreading skin infection and systemic symptoms should be referred to hospital immediately.

Stevens-Johnson syndrome and toxic epidermal necrolysis (TEN) are severe drug reactions causing extensive blistering and loss of skin. They are associated with certain medications (particularly sulfa drugs, anticonvulsants, and allopurinol). Emergency hospitalization is required.

Extensive burns involving the face, hands, genitals, or large body surface areas require urgent assessment and management at a hospital with burn care capabilities.

Eczema herpeticum — herpes simplex virus infection spreading across eczematous skin — presents as clusters of punched-out erosions with fever. Immediate antiviral treatment is required.

Community health workers should be trained to recognize these emergency presentations and to facilitate rapid transfer to appropriate hospital-level care without delay.
""",
}

def write_chunks():
    count = 0
    for fname, content in CHUNKS.items():
        path = os.path.join(OUT, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        count += 1
    print(f"Written {count} chunks to {OUT}")

if __name__ == "__main__":
    write_chunks()
