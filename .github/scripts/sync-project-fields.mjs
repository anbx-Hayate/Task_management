/**
 * Issue テンプレートの値を GitHub Projects フィールドへ同期する
 */

function sq(query) {
  return query.replace(/\s+/g, " ").trim();
}

export function parseIssueField(body, heading) {
  if (!body) return null;
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const patterns = [
    new RegExp(`###\\s*${escaped}[^\\n]*\\n+\\s*([^\\n#]+)`, "i"),
    new RegExp(`\\*\\*${escaped}\\*\\*\\s*\\n+\\s*([^\\n#]+)`, "i"),
  ];
  for (const pattern of patterns) {
    const match = body.match(pattern);
    if (match?.[1]) {
      const value = match[1].trim();
      if (value && !value.startsWith("_No response_")) return value;
    }
  }
  return null;
}

export async function getProjectFields(graphql, projectId) {
  const query = `
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
            }
          }
        }
      }
    }
  `;
  const data = await graphql(sq(query), { projectId });
  const map = new Map();
  for (const field of data.node.fields.nodes) {
    if (field?.name) map.set(field.name, field);
  }
  return map;
}

export async function getIssueNodeId(graphql, owner, repo, issueNumber) {
  const query = `
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) { id }
      }
    }
  `;
  const data = await graphql(sq(query), { owner, repo, number: issueNumber });
  return data.repository.issue.id;
}

export async function getOrAddProjectItem(graphql, projectId, contentId) {
  const findQuery = `
    query($contentId: ID!) {
      node(id: $contentId) {
        ... on Issue {
          projectItems(first: 20) {
            nodes {
              id
              project { id }
            }
          }
        }
      }
    }
  `;
  const found = await graphql(sq(findQuery), { contentId });
  const existing = found.node.projectItems.nodes.find(
    (item) => item.project.id === projectId
  );
  if (existing) return existing.id;

  const addMutation = `
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) {
        item { id }
      }
    }
  `;
  const added = await graphql(sq(addMutation), { projectId, contentId });
  return added.addProjectV2ItemById.item.id;
}

export async function setSingleSelectField(
  graphql,
  projectId,
  itemId,
  fieldId,
  optionId
) {
  const mutation = `
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item { id }
      }
    }
  `;
  await graphql(sq(mutation), { projectId, itemId, fieldId, optionId });
}

export async function syncIssueToProject({
  graphql,
  config,
  owner,
  repo,
  issueNumber,
  issueBody,
}) {
  const fieldMap = await getProjectFields(graphql, config.projectId);
  const issueId = await getIssueNodeId(graphql, owner, repo, issueNumber);
  const itemId = await getOrAddProjectItem(graphql, config.projectId, issueId);

  const updates = [];

  for (const { issueHeading, projectField } of config.parseFields) {
    const value = parseIssueField(issueBody, issueHeading);
    if (!value) continue;
    const field = fieldMap.get(projectField);
    if (!field) continue;
    const option = field.options.find((o) => o.name === value);
    if (!option) continue;
    await setSingleSelectField(
      graphql,
      config.projectId,
      itemId,
      field.id,
      option.id
    );
    updates.push(`${projectField}=${value}`);
  }

  for (const { projectField, value } of config.defaults) {
    const field = fieldMap.get(projectField);
    if (!field) continue;
    const option = field.options.find((o) => o.name === value);
    if (!option) continue;
    await setSingleSelectField(
      graphql,
      config.projectId,
      itemId,
      field.id,
      option.id
    );
    updates.push(`${projectField}=${value}`);
  }

  return updates;
}
