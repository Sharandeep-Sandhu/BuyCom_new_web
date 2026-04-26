"""
Seed all categories and products from the Buy Commodity brochure.
Run with:  python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product


SEED = [
    {
        'name': 'Mild Steel',
        'slug': 'mild-steel',
        'description': 'Premium Hot Rolled and Cold Rolled steel products for manufacturing, fabrication and construction.',
        'icon': '🔩',
        'order': 1,
        'products': [
            {
                'name': 'HR Coil',
                'description': 'Hot Rolled Coils — versatile for automotive, pipe making and diverse industrial applications.',
                'thickness_range': '1.6 – 16 mm',
                'width_range': '900 – 1850 mm',
                'length_range': 'Full Size',
                'grade': 'Grade 1 (IS10748) | Grade 2 (IS1079DD) | E250 (IS2062) | E350 (IS2062) | SAPH440 | BSK 46 | IS1079',
                'order': 1,
            },
            {
                'name': 'HR Sheets',
                'description': 'Hot Rolled Sheets available in standard and custom cut-to-size formats.',
                'thickness_range': '1.6 – 4 mm',
                'width_range': '900 – 1850 mm',
                'length_range': '1500 – 6300 mm',
                'order': 2,
            },
            {
                'name': 'HR Plates',
                'description': 'Heavy Hot Rolled Plates for structural, pressure vessel and shipbuilding applications.',
                'thickness_range': '5 – 10 mm',
                'width_range': '1250 – 1850 mm',
                'length_range': '2500 – 12000 mm',
                'order': 3,
            },
            {
                'name': 'CR Coil',
                'description': 'Cold Rolled Coils offering superior surface finish for appliances, automotive panels and furniture.',
                'thickness_range': '0.5 – 2.5 mm',
                'width_range': '900 – 1520 mm',
                'length_range': 'Full Size',
                'grade': 'CR2 (D) | CR3 (DD) | CR4 (EDD)',
                'order': 4,
            },
            {
                'name': 'CR Sheet',
                'description': 'Cold Rolled Sheets with consistent thickness and smooth surface finish.',
                'thickness_range': '0.5 – 2.5 mm',
                'width_range': '900 – 1520 mm',
                'length_range': '1500 – 6300 mm',
                'grade': 'CR2 (D) | CR3 (DD) | CR4 (EDD)',
                'order': 5,
            },
        ],
    },
    {
        'name': 'Structural Steel',
        'slug': 'structural-steel',
        'description': 'Full range of structural steel sections for construction, infrastructure and heavy engineering projects.',
        'icon': '🏗️',
        'order': 2,
        'products': [
            {
                'name': 'Flat',
                'description': 'Steel flats for fabrication, frames and general engineering use.',
                'thickness_range': '5 – 65 mm',
                'width_range': '25 – 500 mm',
                'order': 1,
            },
            {
                'name': 'Angle',
                'description': 'Equal and unequal leg angles for structural and support applications.',
                'thickness_range': '3 – 20 mm',
                'width_range': '20 – 200 mm',
                'order': 2,
            },
            {
                'name': 'Channel (ISMC)',
                'description': 'Indian Standard Medium Weight Channels for beams, purlins and structural framing.',
                'size_info': '75×40 | 100×50 | 125×65 | 150×75 | 175×75 | 200×75 | 225×80 | 250×80 | 300×90 | 350×100 | 400×100',
                'order': 3,
            },
            {
                'name': 'Beam (ISMB)',
                'description': 'Indian Standard Medium Weight Beams for columns and structural members.',
                'size_info': '100×50 | 125×70 | 150×75 | 175×85 | 200×100 | 225×110 | 250×125 | 300×140 | 350×140 | 400×140 | 450×150 | 500×180 | 550×190 | 600×210',
                'order': 4,
            },
            {
                'name': 'Round Bar',
                'description': 'Solid round bars for shafts, pins, fasteners and general engineering.',
                'size_info': '16 | 18 | 20 | 22 | 25 | 28 | 30 | 32 | 34 | 36 | 38 | 40 | 42 | 45 | 47 | 50 | 56 | 60 | 63 | 66 | 71 | 75 | 80 | 85 | 90 | 100 | 110 | 118 | 125 | 130 | 155 mm',
                'order': 5,
            },
            {
                'name': 'Square Bar',
                'description': 'Solid square bars for keys, clamps and ornamental applications.',
                'size_info': '6 | 16 | 18 | 20 | 22 | 25 | 28 | 32 | 36 | 40 | 45 | 50 | 55 mm',
                'order': 6,
            },
            {
                'name': 'Hollow Pipe (Round & Square)',
                'description': 'Round and square hollow sections for structural and mechanical applications.',
                'size_info': '0.5" | 0.75" | 1.00" | 1.25" | 1.50" | 2.00"',
                'order': 7,
            },
        ],
    },
    {
        'name': 'TMT',
        'slug': 'tmt',
        'description': 'Thermo-Mechanically Treated bars for reinforced concrete construction — superior strength and ductility.',
        'icon': '⚙️',
        'order': 3,
        'products': [
            {
                'name': 'TMT Bars',
                'description': 'High-strength TMT reinforcement bars conforming to IS 1786 for RCC structures, bridges and foundations.',
                'size_info': '6 | 8 | 10 | 12 | 16 | 20 | 22 | 25 | 28 | 32 | 36 | 40 mm',
                'grade': 'Fe 415 | Fe 500 | Fe 500D | Fe 550 | Fe 550D | Fe 600',
                'order': 1,
            },
        ],
    },
    {
        'name': 'Stainless Steel',
        'slug': 'stainless-steel',
        'description': 'Wide range of stainless steel products for food processing, pharma, architecture and marine applications.',
        'icon': '✨',
        'order': 4,
        'products': [
            {
                'name': 'SS Coil',
                'description': 'Stainless steel coils for deep drawing, forming and roll-forming applications.',
                'thickness_range': '2.0 – 12.0 mm',
                'width_range': '1250 mm',
                'grade': '304 | JT | SDM | DD | CU | J4 | JSL-AUS',
                'order': 1,
            },
            {
                'name': 'SS Sheet',
                'description': 'Stainless steel sheets in various finishes for architectural and industrial use.',
                'thickness_range': '0.5 – 6.0 mm',
                'width_range': '1250 mm',
                'grade': '304 | 316 | 202',
                'order': 2,
            },
            {
                'name': 'SS Plate',
                'description': 'Heavy stainless steel plates for pressure vessels, tanks and structural applications.',
                'thickness_range': '8.0 – 80.0 mm',
                'width_range': '1250 mm',
                'grade': '304 | 316',
                'order': 3,
            },
            {
                'name': 'SS HRAP Coil',
                'description': 'Hot Rolled Annealed & Pickled stainless coils for welded tube and structural use.',
                'thickness_range': '2.0 – 6.0 mm',
                'width_range': '1250 mm',
                'grade': '304',
                'order': 4,
            },
            {
                'name': 'SS CRAP Coil',
                'description': 'Cold Rolled Annealed & Pickled coils for precision applications.',
                'thickness_range': '0.5 – 3.0 mm',
                'width_range': '1250 mm',
                'grade': '304',
                'order': 5,
            },
            {
                'name': 'SS Slab',
                'description': 'Semi-finished stainless slabs for rolling mills and further processing.',
                'thickness_range': 'Max 200 mm',
                'width_range': '1285 mm',
                'grade': '304',
                'order': 6,
            },
            {
                'name': 'SS Round Bar',
                'description': 'Stainless round bars for shafts, fasteners and machined components.',
                'thickness_range': '5.0 – 350.0 mm',
                'grade': '304 | 316 | 202',
                'order': 7,
            },
            {
                'name': 'SS Pipe (Round / Square / Rectangle)',
                'description': 'Stainless steel pipes for plumbing, food processing and structural applications.',
                'grade': '202 | 304',
                'order': 8,
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed the database with Buy Commodity categories and products.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Buy Commodity data…'))

        for cat_data in SEED:
            products = cat_data.pop('products')
            cat, created = Category.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data,
            )
            label = 'Created' if created else 'Updated'
            self.stdout.write(f'  {label} category: {cat.name}')

            for i, p in enumerate(products):
                slug = slugify(f"{cat_data['slug']}-{p['name']}")[:250]
                # First product in each category is featured on the homepage
                p.setdefault('is_featured', i == 0)
                Product.objects.update_or_create(
                    slug=slug,
                    defaults={**p, 'category': cat},
                )
                self.stdout.write(f'    ↳ {p["name"]}{"  ★ featured" if p["is_featured"] else ""}')

            cat_data['products'] = products  # restore for next run

        self.stdout.write(self.style.SUCCESS('\n✅  Seed complete!'))