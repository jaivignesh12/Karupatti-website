# Karupatti Royale Design System

This design system centers on "Earthy Luxury," a synthesis of ancestral craftsmanship and modern premium aesthetics. The brand identity is rooted in the "Liquid Gold" of the palm tree, evoking an emotional response of warmth, authenticity, and high-end exclusivity. 

The visual style is a sophisticated hybrid of **Glassmorphism** and **Tactile/Skeuomorphic** depth. We utilize translucent surfaces to mimic the clarity of refined nectar, layered over organic textures like palm leaf grains and cinematic bark shadows. The experience should feel like walking through a sun-drenched palm grove at dusk—high contrast, deep shadows, and glowing highlights that emphasize the artisanal nature of the product.

## Colors

The palette is anchored in **Dark Cocoa**, serving as a canvas that allows the **Jaggery Golden Brown** and **Gold Dust** accents to appear luminous. 

- **Primary & Accent:** Use Jaggery Golden Brown for critical interactive elements. Gold Dust is reserved for micro-interactions, iconography highlights, and premium badging to simulate the shimmer of crystallized sugar.
- **Background Strategy:** The system employs a "Chiaroscuro" approach. Marketing sections alternate between the deep Dark Cocoa (dark mode) and Warm Beige (light mode) to create a rhythmic, editorial flow.
- **Natural Integration:** Soft Palm Leaf Green is used sparingly for organic certification markers and sustainability messaging, ensuring it feels like a natural part of the ecosystem rather than a functional alert color.

## Typography

Typography is used to reinforce the "Premium Village" aesthetic. 

- **Headlines:** Noto Serif provides the literary, traditional authority required for a luxury heritage brand. Use "Display" sizes for product names and hero sections with tighter tracking to emphasize the high-contrast strokes.
- **Body & Interface:** Be Vietnam Pro offers a contemporary, approachable contrast. It maintains high legibility against textured backgrounds.
- **Stylistic Note:** Labels and sub-headers should utilize the "label-caps" style with increased letter spacing to evoke the feeling of high-end apothecary packaging.

## Layout & Spacing

This design system uses a **Fixed Grid** model for desktop to maintain a boutique, editorial feel, transitioning to a fluid system for smaller breakpoints. 

- **Rhythm:** An 8px base unit drives all spacing. For luxury appeal, we prioritize generous vertical white space (using the `section-gap`) to allow the high-quality product photography and 3D elements to "breathe."
- **Composition:** Asymmetric layouts should be used for storytelling sections, where text and imagery overlap to create depth. Standard e-commerce grids (4-column for desktop, 2-column for mobile) apply only to product listing pages.

## Elevation & Depth

Hierarchy is established through **Earthy Glassmorphism** and cinematic lighting.

- **The Glass Effect:** UI containers (cards, modals, navigation) use a semi-transparent fill of Natural Sand or Dark Cocoa with a 20px backdrop blur. This allows the organic textures of the background to peek through, creating a sense of physical layering.
- **Lighting:** Elements are treated as 3D objects. Primary buttons should have a subtle top-down inner glow (#FFD700 at 20% opacity) to simulate sunlight hitting the edge of a golden liquid.
- **Shadows:** Use long, diffused ambient shadows with a hint of Palm Tree Bark Brown (#4E3629) instead of pure black to maintain a warm, organic feel.

## Shapes

The shape language is "Soft-Geometric." While the overall aesthetic is premium and structured, we avoid harsh 90-degree angles to remain approachable and natural.

- **Corners:** Use "Soft" (0.25rem - 0.75rem) radii. This mimics the hand-carved nature of traditional jaggery molds.
- **Decorative Elements:** Use organic, non-geometric masks for image placeholders—specifically shapes resembling the silhouette of a palm frond or a hand-poured drop of syrup.
- **Containers:** Interactive cards should use the `rounded-lg` (0.5rem) setting to ensure they feel substantial and premium.

## Components

- **Buttons:** Primary buttons use a solid Jaggery Golden Brown fill with a subtle "Gold Dust" grain texture. Secondary buttons use a glassmorphic style with a 1px border in Natural Sand.
- **Cards:** Product cards must feature a "floating" shadow. The image should slightly overflow the container to emphasize the 3D depth.
- **Input Fields:** Use a "Minimalist Tray" style—only a bottom border in Natural Sand, which glows Jaggery Golden Brown upon focus.
- **Chips/Badges:** Use the Soft Palm Leaf Green for organic/origin badges, styled as small, pill-shaped glass elements.
- **Specialty Component - "The Provenance Scroller":** A horizontal list component featuring high-fidelity 3D renders of the palm tree bark and the boiling process, used to tell the product's origin story.
- **Interactive Textures:** Use a "Grain Overlay" on top-level headers to give them a tactile, paper-like quality.
