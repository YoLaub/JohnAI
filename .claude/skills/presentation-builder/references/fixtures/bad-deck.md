---
marp: true
theme: presentation
paginate: true
---
## Architecture logicielle
- La couche présentation reçoit la requête
- L'application orchestre les use cases
- Le domaine contient les règles
- L'infrastructure implémente Prisma
- Le repository fait le lien
- On a aussi Redis et pgvector
---
## Sécurité
```ts
export async function createAdherentAction(input: CreateAdherentInput) {
  if (!(await checkRateLimit('adhesion'))) return { error: 'Trop de tentatives.' };
  if (!(await verifyHCaptcha(input.hcaptchaToken))) return { error: 'hCaptcha' };
  const parsed = CreateAdherentSchema.safeParse(input);
  if (!parsed.success) return { errors: parsed.error.flatten().fieldErrors };
  const { membre } = await createAdherentUseCase({});
  return { success: true };
}
```
---
## Résultats
- Couverture passée à 92,7 % exactement
