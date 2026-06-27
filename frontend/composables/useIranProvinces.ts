import { IRAN_PROVINCES_AND_CITIES } from '~/data/iran-provinces-cities'

export { IRAN_PROVINCES_AND_CITIES }

export function useIranProvinces() {
  const provincesAndCities = IRAN_PROVINCES_AND_CITIES

  function citiesForProvince(province: string) {
    return provincesAndCities[province] || []
  }

  return { provincesAndCities, citiesForProvince }
}
