import type { StyleSpecification } from 'maplibre-gl';

/**
 * Transforma o estilo "positron" do OpenFreeMap no visual fino do site
 * (SPEC §6 e guia de implementação §4): fundo branco, ruas em traço fino,
 * quase nenhum preenchimento e rótulos pequenos.
 *
 * Por que mexer no estilo em código e não escrever um estilo próprio: o positron
 * já traz as fontes (glyphs), as fontes de dados e a ordem das camadas certas.
 * Aqui só trocamos cores, espessuras e escondemos o que polui.
 *
 * Cuidado ao mudar: as cores abaixo são os tokens de `estilos/tokens.css`
 * repetidos em hexadecimal, porque o MapLibre pinta numa <canvas> e não lê
 * variáveis CSS. Se um token mudar, mude aqui também.
 */

const COR = {
	branco: '#ffffff',
	agua: '#e8f1ea', // --bg-hero
	linhaVerde: '#9dbfa8', // contorno de parque e rios
	ruaMenor: '#eef2ef',
	ruaMaior: '#dce3dd', // --line-soft
	ruaExpressa: '#c9d3cc', // --line
	rotulo: '#5b6b61' // --muted
} as const;

type Camada = StyleSpecification['layers'][number];

/** Camadas que somem por completo: o mapa fica só com água, parques, ruas e nomes. */
function deveEsconder(camada: Camada): boolean {
	const id = camada.id;
	return (
		('source' in camada && camada.source === 'ne2_shaded') || // raster de relevo
		id === 'building' ||
		id.startsWith('landcover_') ||
		id === 'landuse_residential' ||
		id.startsWith('aeroway') ||
		id.startsWith('boundary_') ||
		id.startsWith('railway') ||
		id.startsWith('highway-shield') ||
		id === 'road_shield_us' ||
		id === 'airport' ||
		id.endsWith('_casing') // contornos das ruas: o traço único já basta
	);
}

/**
 * Espessura em pixels que cresce com o zoom. Valor fixo ficaria grosso demais
 * no zoom da cidade inteira e fino demais perto da rua.
 */
function espessura(base: number) {
	return ['interpolate', ['linear'], ['zoom'], 10, base * 0.5, 16, base * 1.4] as never;
}

export function estilizarMapa(estilo: StyleSpecification): StyleSpecification {
	const camadas: Camada[] = [];

	for (const camada of estilo.layers) {
		const id = camada.id;

		// Escondemos em vez de remover: assim a ordem e as referências do estilo ficam intactas.
		if (deveEsconder(camada)) {
			camadas.push({ ...camada, layout: { ...camada.layout, visibility: 'none' } } as Camada);
			continue;
		}

		// Cada camada vira uma cópia com a pintura trocada; o estilo original não é alterado.
		const pintura: Record<string, unknown> = { ...('paint' in camada ? camada.paint : {}) };
		const layout: Record<string, unknown> = { ...('layout' in camada ? camada.layout : {}) };

		if (id === 'background') {
			pintura['background-color'] = COR.branco;
		} else if (id === 'park') {
			// Parque só com contorno: nada de mancha verde.
			pintura['fill-color'] = 'rgba(255, 255, 255, 0)';
			pintura['fill-outline-color'] = COR.linhaVerde;
		} else if (id === 'water') {
			pintura['fill-color'] = COR.agua;
			pintura['fill-antialias'] = true;
		} else if (id === 'waterway') {
			pintura['line-color'] = COR.linhaVerde;
			pintura['line-width'] = espessura(1.5);
		} else if (id === 'highway_path' || id === 'highway_minor') {
			pintura['line-color'] = COR.ruaMenor;
			pintura['line-opacity'] = 1;
			pintura['line-width'] = espessura(1);
		} else if (id.startsWith('highway_major')) {
			pintura['line-color'] = COR.ruaMaior;
			pintura['line-width'] = espessura(2);
		} else if (id.includes('motorway')) {
			// Também cobre os túneis e pontes de via expressa.
			pintura['line-color'] = COR.ruaExpressa;
			pintura['line-width'] = espessura(2.5);
		} else if (id === 'road_pier') {
			pintura['line-color'] = COR.ruaMaior;
		} else if (id === 'road_area_pier') {
			pintura['fill-color'] = COR.ruaMenor;
		} else if (camada.type === 'symbol') {
			// Rótulos: cinza do site, halo branco e texto pequeno. A fonte (text-font)
			// do estilo é mantida porque ela precisa existir no servidor de glyphs.
			pintura['text-color'] = COR.rotulo;
			pintura['text-halo-color'] = COR.branco;
			pintura['text-halo-width'] = 1.2;
			pintura['text-halo-blur'] = 0;
			layout['text-size'] = id.startsWith('highway-name') || id === 'label_other' ? 10 : 12;
		}

		camadas.push({ ...camada, paint: pintura, layout } as Camada);
	}

	return { ...estilo, layers: camadas };
}
